/**
 * Match LinkedIn's official connections CSV export to BGE geek frontmatter.
 *
 * The model stores only candidate public profile URLs and BGE names. It never
 * persists the source CSV, email addresses, companies, or job titles.
 *
 * @module
 */
import { z } from "npm:zod@4";

const GlobalArgsSchema = z.object({
  geeksDir: z.string().min(1).default("_geeks"),
});
const AnalyzeArgsSchema = z.object({
  csvPath: z.string().min(1),
  urlColumn: z.string().optional(),
  geekName: z.string().optional(),
});
const ApplyArgsSchema = z.object({});

const CandidateSchema = z.object({
  geekName: z.string(),
  geekFile: z.string(),
  linkedInUrl: z.string().url(),
  sourceRow: z.number().int().positive(),
  fileHash: z.string().regex(/^[a-f0-9]{64}$/),
});
const ConflictSchema = z.object({
  geekName: z.string(),
  geekFile: z.string(),
  existingUrl: z.string(),
  candidateUrl: z.string(),
  reason: z.string(),
});
const AnalysisSchema = z.object({
  csvFileName: z.string(),
  headerRow: z.number().int().positive(),
  columns: z.object({
    firstName: z.string(),
    lastName: z.string(),
    linkedInUrl: z.string().nullable(),
  }),
  counts: z.object({
    geekFiles: z.number().int().nonnegative(),
    connectionRows: z.number().int().nonnegative(),
    exactCandidates: z.number().int().nonnegative(),
    alreadyCurrent: z.number().int().nonnegative(),
    conflicts: z.number().int().nonnegative(),
    ambiguous: z.number().int().nonnegative(),
    unmatchedGeeks: z.number().int().nonnegative(),
    matchedWithoutUrl: z.number().int().nonnegative(),
    invalidUrls: z.number().int().nonnegative(),
  }),
  candidates: z.array(CandidateSchema),
  conflicts: z.array(ConflictSchema),
  ambiguousGeeks: z.array(z.string()),
  unmatchedGeeks: z.array(z.string()),
  warnings: z.array(z.string()),
  analyzedAt: z.iso.datetime(),
});
const ApplyResultSchema = z.object({
  attempted: z.number().int().nonnegative(),
  updated: z.number().int().nonnegative(),
  unchanged: z.number().int().nonnegative(),
  skipped: z.number().int().nonnegative(),
  updatedGeeks: z.array(z.string()),
  warnings: z.array(z.string()),
  appliedAt: z.iso.datetime(),
});

type GlobalArgs = z.infer<typeof GlobalArgsSchema>;
type Analysis = z.infer<typeof AnalysisSchema>;
type Candidate = z.infer<typeof CandidateSchema>;
type ResourceHandle = { name: string; specName?: string; version?: number };
type Logger = {
  info(message: string, ...args: unknown[]): void;
  warning(message: string, ...args: unknown[]): void;
};
type AnalyzeContext = {
  repoDir: string;
  globalArgs: GlobalArgs;
  logger: Logger;
  writeResource: (
    specName: string,
    name: string,
    data: Record<string, unknown>,
  ) => Promise<ResourceHandle>;
};
type ApplyContext = AnalyzeContext & {
  readResource: (
    instanceName: string,
    version?: number,
  ) => Promise<Record<string, unknown> | null>;
};
type GeekRecord = {
  name: string;
  normalizedName: string;
  relativePath: string;
  fileHash: string;
  linkedInUrl: string | null;
};
type ConnectionRecord = {
  normalizedName: string;
  linkedInUrl: string | null;
  sourceRow: number;
  invalidUrl: boolean;
};

const FIRST_NAME_HEADERS = new Set(["firstname", "givenname", "nome"]);
const LAST_NAME_HEADERS = new Set([
  "lastname",
  "surname",
  "familyname",
  "cognome",
]);
const URL_HEADERS = new Set([
  "url",
  "profileurl",
  "publicprofileurl",
  "linkedin",
  "linkedinurl",
  "linkedinprofile",
  "linkedinprofileurl",
]);

/** Normalize a display name for conservative exact matching. */
function normalizeName(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .toLocaleLowerCase("it")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function normalizeHeader(value: string): string {
  return value
    .replace(/^\uFEFF/, "")
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "");
}

/** Parse RFC 4180-style CSV, including quoted commas and embedded newlines. */
function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"') {
        if (text[index + 1] === '"') {
          field += '"';
          index += 1;
        } else quoted = false;
      } else field += char;
      continue;
    }
    if (char === '"' && field.length === 0) quoted = true;
    else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else field += char;
  }
  if (quoted) throw new Error("CSV contains an unterminated quoted field");
  if (field.length > 0 || row.length > 0) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows;
}

/** Convert a supported LinkedIn member URL to a stable public URL. */
function normalizeLinkedInUrl(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const withScheme = /^https?:\/\//i.test(trimmed)
    ? trimmed
    : `https://${trimmed}`;
  try {
    const parsed = new URL(withScheme);
    const host = parsed.hostname.toLowerCase();
    if (
      host !== "linkedin.com" && host !== "www.linkedin.com" &&
      !host.endsWith(".linkedin.com")
    ) return null;
    if (!/^\/(in|pub)\/[^/]+\/?$/i.test(parsed.pathname)) return null;
    return `https://www.linkedin.com${parsed.pathname.replace(/\/+$/, "")}/`;
  } catch {
    return null;
  }
}

function parseYamlScalar(value: string): string {
  const trimmed = value.trim();
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    const inner = trimmed.slice(1, -1);
    return trimmed[0] === "'"
      ? inner.replace(/''/g, "'")
      : inner.replace(/\\"/g, '"');
  }
  return trimmed;
}

function getFrontmatter(content: string): string {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!match) throw new Error("missing YAML frontmatter");
  return match[1];
}

function getGeekName(frontmatter: string): string {
  const match = frontmatter.match(/^nome:\s*(.+?)\s*$/m);
  if (!match) throw new Error("missing nome field");
  const value = parseYamlScalar(match[1]);
  if (!value) throw new Error("empty nome field");
  return value;
}

/** Find an existing LinkedIn/Linkedin entry without parsing unrelated YAML. */
function getExistingLinkedIn(frontmatter: string): string | null {
  const lines = frontmatter.split(/\r?\n/);
  const linksIndex = lines.findIndex((line) => /^links:\s*$/.test(line));
  if (linksIndex < 0) return null;
  for (let index = linksIndex + 1; index < lines.length; index += 1) {
    const line = lines[index];
    if (line && !/^\s/.test(line)) break;
    const match = line.match(/^\s+([^:]+):\s*(.*?)\s*$/);
    if (match && normalizeHeader(match[1]) === "linkedin") {
      return parseYamlScalar(match[2]);
    }
  }
  return null;
}

/** Insert a LinkedIn entry while preserving unrelated content. */
function addLinkedInLink(content: string, url: string): string {
  const frontmatter = getFrontmatter(content);
  const lines = frontmatter.split(/\r?\n/);
  const linksIndex = lines.findIndex((line) => /^links:\s*$/.test(line));
  if (linksIndex >= 0) {
    let insertAt = linksIndex + 1;
    while (
      insertAt < lines.length &&
      (!lines[insertAt] || /^\s/.test(lines[insertAt]))
    ) insertAt += 1;
    lines.splice(insertAt, 0, `  LinkedIn: ${url}`);
  } else {
    const nameIndex = lines.findIndex((line) => /^nome:/.test(line));
    lines.splice(
      nameIndex >= 0 ? nameIndex : lines.length,
      0,
      "links:",
      `  LinkedIn: ${url}`,
    );
  }
  return content.replace(frontmatter, lines.join("\n"));
}

async function sha256(content: string): Promise<string> {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(content),
  );
  return Array.from(new Uint8Array(digest)).map((byte) =>
    byte.toString(16).padStart(2, "0")
  ).join("");
}

async function resolveGeeksDir(
  repoDir: string,
  configured: string,
): Promise<string> {
  const repoReal = await Deno.realPath(repoDir);
  const candidate = configured.startsWith("/")
    ? configured
    : `${repoReal}/${configured}`;
  const geeksReal = await Deno.realPath(candidate);
  const prefix = repoReal.endsWith("/") ? repoReal : `${repoReal}/`;
  if (geeksReal !== repoReal && !geeksReal.startsWith(prefix)) {
    throw new Error(`geeksDir must be inside the repository: ${configured}`);
  }
  return geeksReal;
}

function resolveCsvPath(repoDir: string, csvPath: string): string {
  return csvPath.startsWith("/") ? csvPath : `${repoDir}/${csvPath}`;
}

function baseName(path: string): string {
  return path.replace(/\\/g, "/").split("/").filter(Boolean).at(-1) ?? path;
}

function groupByName<T extends { normalizedName: string }>(
  items: T[],
): Map<string, T[]> {
  const groups = new Map<string, T[]>();
  for (const item of items) {
    groups.set(item.normalizedName, [
      ...(groups.get(item.normalizedName) ?? []),
      item,
    ]);
  }
  return groups;
}

/** Load all geek Markdown files in one fan-out scan. */
async function loadGeeks(
  repoDir: string,
  geeksDir: string,
): Promise<{ geeks: GeekRecord[]; warnings: string[] }> {
  const geeks: GeekRecord[] = [];
  const warnings: string[] = [];
  const root = await resolveGeeksDir(repoDir, geeksDir);
  const entries: Deno.DirEntry[] = [];
  for await (const entry of Deno.readDir(root)) {
    if (entry.isFile && entry.name.endsWith(".md")) entries.push(entry);
  }
  entries.sort((left, right) => left.name.localeCompare(right.name, "it"));
  for (const entry of entries) {
    try {
      const content = await Deno.readTextFile(`${root}/${entry.name}`);
      const frontmatter = getFrontmatter(content);
      const name = getGeekName(frontmatter);
      geeks.push({
        name,
        normalizedName: normalizeName(name),
        relativePath: `${geeksDir.replace(/\/+$/, "")}/${entry.name}`,
        fileHash: await sha256(content),
        linkedInUrl: getExistingLinkedIn(frontmatter),
      });
    } catch (error) {
      warnings.push(
        `${entry.name}: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    }
  }
  return { geeks, warnings };
}

type Columns = {
  headerRowIndex: number;
  firstNameIndex: number;
  lastNameIndex: number;
  urlIndex: number | null;
  firstNameLabel: string;
  lastNameLabel: string;
  urlLabel: string | null;
};

/** Identify export columns even when LinkedIn adds notice rows. */
function locateColumns(rows: string[][], explicitUrlColumn?: string): Columns {
  const explicit = explicitUrlColumn
    ? normalizeHeader(explicitUrlColumn)
    : null;
  for (let rowIndex = 0; rowIndex < rows.length; rowIndex += 1) {
    const normalized = rows[rowIndex].map(normalizeHeader);
    const firstNameIndex = normalized.findIndex((value) =>
      FIRST_NAME_HEADERS.has(value)
    );
    const lastNameIndex = normalized.findIndex((value) =>
      LAST_NAME_HEADERS.has(value)
    );
    if (firstNameIndex < 0 || lastNameIndex < 0) continue;
    const foundUrl = explicit
      ? normalized.findIndex((value) => value === explicit)
      : normalized.findIndex((value) => URL_HEADERS.has(value));
    if (explicit && foundUrl < 0) {
      throw new Error(`Requested URL column not found: ${explicitUrlColumn}`);
    }
    return {
      headerRowIndex: rowIndex,
      firstNameIndex,
      lastNameIndex,
      urlIndex: foundUrl >= 0 ? foundUrl : null,
      firstNameLabel: rows[rowIndex][firstNameIndex],
      lastNameLabel: rows[rowIndex][lastNameIndex],
      urlLabel: foundUrl >= 0 ? rows[rowIndex][foundUrl] : null,
    };
  }
  throw new Error("Could not find First Name and Last Name columns in the CSV");
}

function loadConnections(
  rows: string[][],
  columns: Columns,
): ConnectionRecord[] {
  const records: ConnectionRecord[] = [];
  for (
    let index = columns.headerRowIndex + 1;
    index < rows.length;
    index += 1
  ) {
    const firstName = (rows[index][columns.firstNameIndex] ?? "").trim();
    const lastName = (rows[index][columns.lastNameIndex] ?? "").trim();
    if (!firstName && !lastName) continue;
    const rawUrl = columns.urlIndex === null
      ? ""
      : (rows[index][columns.urlIndex] ?? "").trim();
    const linkedInUrl = rawUrl ? normalizeLinkedInUrl(rawUrl) : null;
    records.push({
      normalizedName: normalizeName(`${firstName} ${lastName}`.trim()),
      linkedInUrl,
      sourceRow: index + 1,
      invalidUrl: Boolean(rawUrl) && !linkedInUrl,
    });
  }
  return records;
}

/** Analyze an official connections export without mutating the repository. */
async function analyze(
  args: z.infer<typeof AnalyzeArgsSchema>,
  context: AnalyzeContext,
): Promise<{ dataHandles: ResourceHandle[] }> {
  const csvPath = resolveCsvPath(context.repoDir, args.csvPath);
  context.logger.info(
    "Analyzing LinkedIn connections export {csvFile}",
    baseName(csvPath),
  );
  const rows = parseCsv(await Deno.readTextFile(csvPath));
  const columns = locateColumns(rows, args.urlColumn);
  const connections = loadConnections(rows, columns);
  const loaded = await loadGeeks(
    context.repoDir,
    context.globalArgs.geeksDir,
  );
  const targetName = normalizeName(args.geekName ?? "");
  const geeks = targetName
    ? loaded.geeks.filter((geek) => geek.normalizedName === targetName)
    : loaded.geeks;
  if (targetName && geeks.length === 0) {
    throw new Error(`No geek file matches requested name: ${args.geekName}`);
  }
  const warnings = loaded.warnings;
  const geeksByName = groupByName(geeks);
  const connectionsByName = groupByName(connections);
  const candidates: Candidate[] = [];
  const conflicts: z.infer<typeof ConflictSchema>[] = [];
  const ambiguousGeeks = new Set<string>();
  const unmatchedGeeks: string[] = [];
  let alreadyCurrent = 0;
  let matchedWithoutUrl = 0;

  for (const geek of geeks) {
    const geekGroup = geeksByName.get(geek.normalizedName) ?? [];
    const connectionGroup = connectionsByName.get(geek.normalizedName) ?? [];
    if (connectionGroup.length === 0) {
      unmatchedGeeks.push(geek.name);
      continue;
    }
    const validUrls = new Set(
      connectionGroup.map((item) => item.linkedInUrl).filter((
        value,
      ): value is string => Boolean(value)),
    );
    if (
      geekGroup.length !== 1 || connectionGroup.length !== 1 ||
      validUrls.size > 1
    ) {
      ambiguousGeeks.add(geek.name);
      continue;
    }
    if (validUrls.size === 0) {
      matchedWithoutUrl += 1;
      continue;
    }
    const connection = connectionGroup[0];
    const candidateUrl = connection.linkedInUrl as string;
    if (geek.linkedInUrl) {
      if (normalizeLinkedInUrl(geek.linkedInUrl) === candidateUrl) {
        alreadyCurrent += 1;
      } else {conflicts.push({
          geekName: geek.name,
          geekFile: geek.relativePath,
          existingUrl: geek.linkedInUrl,
          candidateUrl,
          reason:
            "Existing LinkedIn link differs; automatic overwrite is disabled",
        });}
      continue;
    }
    candidates.push({
      geekName: geek.name,
      geekFile: geek.relativePath,
      linkedInUrl: candidateUrl,
      sourceRow: connection.sourceRow,
      fileHash: geek.fileHash,
    });
  }

  const byName = (left: { geekName: string }, right: { geekName: string }) =>
    left.geekName.localeCompare(right.geekName, "it");
  candidates.sort(byName);
  conflicts.sort(byName);
  unmatchedGeeks.sort((left, right) => left.localeCompare(right, "it"));
  const analysis: Analysis = {
    csvFileName: baseName(csvPath),
    headerRow: columns.headerRowIndex + 1,
    columns: {
      firstName: columns.firstNameLabel,
      lastName: columns.lastNameLabel,
      linkedInUrl: columns.urlLabel,
    },
    counts: {
      geekFiles: geeks.length,
      connectionRows: connections.length,
      exactCandidates: candidates.length,
      alreadyCurrent,
      conflicts: conflicts.length,
      ambiguous: ambiguousGeeks.size,
      unmatchedGeeks: unmatchedGeeks.length,
      matchedWithoutUrl,
      invalidUrls: connections.filter((item) => item.invalidUrl).length,
    },
    candidates,
    conflicts,
    ambiguousGeeks: [...ambiguousGeeks].sort((left, right) =>
      left.localeCompare(right, "it")
    ),
    unmatchedGeeks,
    warnings,
    analyzedAt: new Date().toISOString(),
  };
  context.logger.info(
    "Analyzed {geeks} geeks and found {candidates} exact candidates",
    analysis.counts.geekFiles,
    analysis.counts.exactCandidates,
  );
  const handle = await context.writeResource(
    "analysis",
    "analysis-current",
    analysis,
  );
  return { dataHandles: [handle] };
}

async function writeAtomically(path: string, content: string): Promise<void> {
  const stat = await Deno.stat(path);
  const tempPath = `${path}.swamp-tmp-${crypto.randomUUID()}`;
  try {
    await Deno.writeTextFile(tempPath, content, { createNew: true });
    if (stat.mode !== null) await Deno.chmod(tempPath, stat.mode);
    await Deno.rename(tempPath, path);
  } catch (error) {
    try {
      await Deno.remove(tempPath);
    } catch {
      // No temporary file remains.
    }
    throw error;
  }
}

/** Apply only exact candidates from the latest manually reviewed analysis. */
async function applyCandidates(
  _args: z.infer<typeof ApplyArgsSchema>,
  context: ApplyContext,
): Promise<{ dataHandles: ResourceHandle[] }> {
  context.logger.info("Applying latest exact LinkedIn candidate set");
  const stored = await context.readResource("analysis-current");
  if (!stored) throw new Error("No analysis found; run analyze first");
  const analysis = AnalysisSchema.parse(stored);
  const geeksRoot = await resolveGeeksDir(
    context.repoDir,
    context.globalArgs.geeksDir,
  );
  const warnings: string[] = [];
  const updatedGeeks: string[] = [];
  let unchanged = 0;
  let skipped = 0;

  for (const candidate of analysis.candidates) {
    const path = `${geeksRoot}/${candidate.geekFile.replace(/^.*\//, "")}`;
    try {
      const realPath = await Deno.realPath(path);
      const rootPrefix = geeksRoot.endsWith("/") ? geeksRoot : `${geeksRoot}/`;
      if (!realPath.startsWith(rootPrefix)) {
        throw new Error("resolved outside geeksDir");
      }
      const content = await Deno.readTextFile(realPath);
      const existing = getExistingLinkedIn(getFrontmatter(content));
      if (existing) {
        if (normalizeLinkedInUrl(existing) === candidate.linkedInUrl) {
          unchanged += 1;
        } else throw new Error("existing LinkedIn link was not overwritten");
        continue;
      }
      if (await sha256(content) !== candidate.fileHash) {
        throw new Error("file changed after analysis");
      }
      await writeAtomically(
        realPath,
        addLinkedInLink(content, candidate.linkedInUrl),
      );
      updatedGeeks.push(candidate.geekName);
    } catch (error) {
      warnings.push(
        `${candidate.geekName}: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
      skipped += 1;
    }
  }

  const result = {
    attempted: analysis.candidates.length,
    updated: updatedGeeks.length,
    unchanged,
    skipped,
    updatedGeeks,
    warnings,
    appliedAt: new Date().toISOString(),
  };
  context.logger.info(
    "Applied {updated} links; {skipped} skipped",
    result.updated,
    result.skipped,
  );
  const handle = await context.writeResource(
    "applyResult",
    "apply-result-current",
    result,
  );
  return { dataHandles: [handle] };
}

/** BGE geek link enrichment model. */
export const model = {
  type: "@alvagante/geek-link-enricher",
  version: "2026.07.30.2",
  globalArguments: GlobalArgsSchema,
  reports: ["@alvagante/geek-link-enrichment-report"],
  resources: {
    analysis: {
      description: "Minimal, reviewable LinkedIn-to-geek match candidates",
      schema: AnalysisSchema,
      lifetime: "infinite",
      garbageCollection: 10,
    },
    applyResult: {
      description: "Result of applying approved exact LinkedIn matches",
      schema: ApplyResultSchema,
      lifetime: "infinite",
      garbageCollection: 10,
    },
  },
  checks: {
    "safe-geeks-directory": {
      description: "Ensure geek files are confined to this repository",
      labels: ["policy"],
      appliesTo: ["update"],
      execute: async (context: { repoDir: string; globalArgs: GlobalArgs }) => {
        try {
          await resolveGeeksDir(context.repoDir, context.globalArgs.geeksDir);
          return { pass: true };
        } catch (error) {
          return {
            pass: false,
            errors: [error instanceof Error ? error.message : String(error)],
          };
        }
      },
    },
  },
  methods: {
    analyze: {
      description:
        "Analyze an official LinkedIn connections CSV and produce exact match candidates",
      arguments: AnalyzeArgsSchema,
      execute: analyze,
    },
    update: {
      description:
        "Apply the latest exact candidates without overwriting or using stale files",
      arguments: ApplyArgsSchema,
      execute: applyCandidates,
    },
  },
};

/** Pure helpers exposed for local unit tests. */
export const testing = {
  addLinkedInLink,
  getExistingLinkedIn,
  normalizeLinkedInUrl,
  normalizeName,
  parseCsv,
};
