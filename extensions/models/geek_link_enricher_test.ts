import { model, testing } from "./geek_link_enricher.ts";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

Deno.test("CSV parser handles notices and quoted commas", () => {
  const rows = testing.parseCsv(
    'LinkedIn export notice\nFirst Name,Last Name,URL\n"Marco, Jr",Guardigli,"https://linkedin.com/in/mgua"\n',
  );
  assert(rows.length === 3, "expected three rows");
  assert(rows[2][0] === "Marco, Jr", "quoted comma was not parsed");
});

Deno.test("CSV parser rejects unterminated quoted fields", () => {
  let message = "";
  try {
    testing.parseCsv(
      `First Name,Last Name,URL\n"Marco,Guardigli,https://linkedin.com/in/mgua`,
    );
  } catch (error) {
    message = error instanceof Error ? error.message : String(error);
  }
  assert(
    message.includes("unterminated quoted field"),
    "malformed CSV was not rejected",
  );
});

Deno.test("LinkedIn URL normalization accepts member profiles only", () => {
  assert(
    testing.normalizeLinkedInUrl(
      "https://it.linkedin.com/in/marcoguardigli?trk=contacts",
    ) === "https://www.linkedin.com/in/marcoguardigli/",
    "expected canonical member URL",
  );
  assert(
    testing.normalizeLinkedInUrl("https://linkedin.com/company/example") ===
      null,
    "company URL must be rejected",
  );
});

Deno.test("analyze and apply honor a one-person privacy-preserving filter", async () => {
  const repoDir = await Deno.makeTempDir();
  const geeksDir = `${repoDir}/_geeks`;
  await Deno.mkdir(geeksDir);
  const geekFile = `${geeksDir}/Marco Guardigli.md`;
  await Deno.writeTextFile(
    geekFile,
    "---\nepisodi:\n- 114\nlayout: geek\nnome: Marco Guardigli\n---\nBio\n",
  );
  const otherGeekFile = `${geeksDir}/Other Geek.md`;
  await Deno.writeTextFile(
    otherGeekFile,
    "---\nlayout: geek\nnome: Other Geek\n---\nBio\n",
  );
  const csvFile = `${repoDir}/Connections.csv`;
  await Deno.writeTextFile(
    csvFile,
    "First Name,Last Name,URL,Email Address\nMarco,Guardigli,https://it.linkedin.com/in/marcoguardigli,private@example.test\nOther,Geek,https://linkedin.com/in/other-geek,other-private@example.test\n",
  );

  let analysis: Record<string, unknown> | null = null;
  const analyze = model.methods.analyze.execute as unknown as (
    args: { csvPath: string; geekName?: string },
    context: Record<string, unknown>,
  ) => Promise<unknown>;
  await analyze({ csvPath: csvFile, geekName: "Marco Guardigli" }, {
    repoDir,
    globalArgs: { geeksDir: "_geeks" },
    logger: { info: () => {}, warning: () => {} },
    writeResource: (
      specName: string,
      name: string,
      data: Record<string, unknown>,
    ) => {
      assert(specName === "analysis", "unexpected analysis spec");
      analysis = data;
      return Promise.resolve({ name, specName });
    },
  });
  assert(analysis !== null, "analysis was not written");
  assert(
    !JSON.stringify(analysis).includes("private@example.test"),
    "email leaked into analysis",
  );
  assert(
    (analysis as { counts: Record<string, number> }).counts.exactCandidates ===
      1,
    "expected one candidate",
  );

  let result: Record<string, unknown> | null = null;
  const apply = model.methods.update.execute as unknown as (
    args: Record<string, never>,
    context: Record<string, unknown>,
  ) => Promise<unknown>;
  await apply({}, {
    repoDir,
    globalArgs: { geeksDir: "_geeks" },
    logger: { info: () => {}, warning: () => {} },
    readResource: () => Promise.resolve(analysis),
    writeResource: (
      specName: string,
      name: string,
      data: Record<string, unknown>,
    ) => {
      assert(specName === "applyResult", "unexpected apply spec");
      result = data;
      return Promise.resolve({ name, specName });
    },
  });
  assert(
    result !== null && (result as { updated: number }).updated === 1,
    "expected one update",
  );
  const updated = await Deno.readTextFile(geekFile);
  assert(
    updated.includes("  LinkedIn: https://www.linkedin.com/in/marcoguardigli/"),
    "link was not inserted",
  );
  assert(
    !(await Deno.readTextFile(otherGeekFile)).includes("LinkedIn:"),
    "filter allowed a second geek to change",
  );

  result = null;
  await apply({}, {
    repoDir,
    globalArgs: { geeksDir: "_geeks" },
    logger: { info: () => {}, warning: () => {} },
    readResource: () => Promise.resolve(analysis),
    writeResource: (
      _specName: string,
      name: string,
      data: Record<string, unknown>,
    ) => {
      result = data;
      return Promise.resolve({ name });
    },
  });
  assert(
    result !== null &&
      (result as { updated: number }).updated === 0 &&
      (result as { unchanged: number }).unchanged === 1,
    "retry should be an unchanged no-op",
  );
});

Deno.test("update skips stale files and conflicting existing links", async () => {
  const repoDir = await Deno.makeTempDir();
  const geeksDir = `${repoDir}/_geeks`;
  await Deno.mkdir(geeksDir);
  const staleFile = `${geeksDir}/Stale Geek.md`;
  const conflictFile = `${geeksDir}/Conflict Geek.md`;
  await Deno.writeTextFile(
    staleFile,
    "---\nlayout: geek\nnome: Stale Geek\n---\nBio\n",
  );
  await Deno.writeTextFile(
    conflictFile,
    "---\nlayout: geek\nnome: Conflict Geek\nlinks:\n  LinkedIn: https://www.linkedin.com/in/existing/\n---\nBio\n",
  );

  const analysis = {
    csvFileName: "Connections.csv",
    headerRow: 1,
    columns: {
      firstName: "First Name",
      lastName: "Last Name",
      linkedInUrl: "URL",
    },
    counts: {
      geekFiles: 2,
      connectionRows: 2,
      exactCandidates: 2,
      alreadyCurrent: 0,
      conflicts: 0,
      ambiguous: 0,
      unmatchedGeeks: 0,
      matchedWithoutUrl: 0,
      invalidUrls: 0,
    },
    candidates: [
      {
        geekName: "Stale Geek",
        geekFile: "_geeks/Stale Geek.md",
        linkedInUrl: "https://www.linkedin.com/in/stale/",
        sourceRow: 2,
        fileHash: "0".repeat(64),
      },
      {
        geekName: "Conflict Geek",
        geekFile: "_geeks/Conflict Geek.md",
        linkedInUrl: "https://www.linkedin.com/in/candidate/",
        sourceRow: 3,
        fileHash: "0".repeat(64),
      },
    ],
    conflicts: [],
    ambiguousGeeks: [],
    unmatchedGeeks: [],
    warnings: [],
    analyzedAt: new Date().toISOString(),
  };

  let result: Record<string, unknown> | null = null;
  const update = model.methods.update.execute as unknown as (
    args: Record<string, never>,
    context: Record<string, unknown>,
  ) => Promise<unknown>;
  await update({}, {
    repoDir,
    globalArgs: { geeksDir: "_geeks" },
    logger: { info: () => {}, warning: () => {} },
    readResource: () => Promise.resolve(analysis),
    writeResource: (
      _specName: string,
      name: string,
      data: Record<string, unknown>,
    ) => {
      result = data;
      return Promise.resolve({ name });
    },
  });

  assert(
    result !== null && (result as { skipped: number }).skipped === 2,
    "unsafe candidates should be skipped",
  );
  const warnings = (result as { warnings: string[] }).warnings.join("\n");
  assert(
    warnings.includes("file changed after analysis"),
    "stale file warning missing",
  );
  assert(warnings.includes("was not overwritten"), "conflict warning missing");
  assert(
    !(await Deno.readTextFile(staleFile)).includes("LinkedIn:"),
    "stale file was changed",
  );
  assert(
    (await Deno.readTextFile(conflictFile)).includes(
      "https://www.linkedin.com/in/existing/",
    ),
    "existing link was overwritten",
  );
});
