/** Human-readable review report for BGE LinkedIn enrichment runs. @module */
type DataHandle = { name: string; specName?: string; version?: number };
type ReportContext = {
  modelType: string;
  modelId: string;
  methodName: string;
  executionStatus: "succeeded" | "failed";
  errorMessage?: string;
  dataHandles: DataHandle[];
  dataRepository: {
    getContent(
      type: string,
      modelId: string,
      dataName: string,
      version?: number,
    ): Promise<Uint8Array | null>;
  };
};
type Analysis = {
  csvFileName: string;
  headerRow: number;
  columns: { firstName: string; lastName: string; linkedInUrl: string | null };
  counts: Record<string, number>;
  candidates: Array<
    {
      geekName: string;
      geekFile: string;
      linkedInUrl: string;
      sourceRow: number;
    }
  >;
  conflicts: Array<
    {
      geekName: string;
      existingUrl: string;
      candidateUrl: string;
      reason: string;
    }
  >;
  ambiguousGeeks: string[];
  unmatchedGeeks: string[];
  warnings: string[];
};
type ApplyResult = {
  attempted: number;
  updated: number;
  unchanged: number;
  skipped: number;
  updatedGeeks: string[];
  warnings: string[];
};

function escapeCell(value: unknown): string {
  return String(value ?? "").replace(/\|/g, "\\|").replace(/\r?\n/g, " ");
}

async function readOutput(
  context: ReportContext,
  specName: string,
): Promise<Record<string, unknown> | null> {
  const handle = context.dataHandles.find((item) => item.specName === specName);
  if (!handle) return null;
  const bytes = await context.dataRepository.getContent(
    context.modelType,
    context.modelId,
    handle.name,
    handle.version,
  );
  return bytes
    ? JSON.parse(new TextDecoder().decode(bytes)) as Record<string, unknown>
    : null;
}

function renderAnalysis(analysis: Analysis): string {
  const lines = [
    "# BGE geek LinkedIn enrichment",
    "",
    `Source: \`${
      escapeCell(analysis.csvFileName)
    }\` (header row ${analysis.headerRow})`,
    "",
    "| Result | Count |",
    "| --- | ---: |",
    `| Geek files | ${analysis.counts.geekFiles ?? 0} |`,
    `| Connection rows | ${analysis.counts.connectionRows ?? 0} |`,
    `| Exact candidates | ${analysis.counts.exactCandidates ?? 0} |`,
    `| Already current | ${analysis.counts.alreadyCurrent ?? 0} |`,
    `| Conflicts | ${analysis.counts.conflicts ?? 0} |`,
    `| Ambiguous | ${analysis.counts.ambiguous ?? 0} |`,
    `| Matched without URL | ${analysis.counts.matchedWithoutUrl ?? 0} |`,
    `| Invalid URLs | ${analysis.counts.invalidUrls ?? 0} |`,
    `| Unmatched geeks | ${analysis.counts.unmatchedGeeks ?? 0} |`,
    "",
  ];
  if (!analysis.columns.linkedInUrl) {
    lines.push(
      "> No recognized LinkedIn URL column was found. Nothing can be applied.",
      "",
    );
  }
  if (analysis.candidates.length > 0) {
    lines.push(
      "## Exact candidates",
      "",
      "| Geek | LinkedIn | CSV row | File |",
      "| --- | --- | ---: | --- |",
    );
    for (const item of analysis.candidates) {
      lines.push(
        `| ${escapeCell(item.geekName)} | ${
          escapeCell(item.linkedInUrl)
        } | ${item.sourceRow} | \`${escapeCell(item.geekFile)}\` |`,
      );
    }
    lines.push("");
  }
  if (analysis.conflicts.length > 0) {
    lines.push(
      "## Conflicts — never applied automatically",
      "",
      "| Geek | Existing | Candidate |",
      "| --- | --- | --- |",
    );
    for (const item of analysis.conflicts) {
      lines.push(
        `| ${escapeCell(item.geekName)} | ${escapeCell(item.existingUrl)} | ${
          escapeCell(item.candidateUrl)
        } |`,
      );
    }
    lines.push("");
  }
  if (analysis.ambiguousGeeks.length > 0) {
    lines.push(
      "## Ambiguous geeks",
      "",
      ...analysis.ambiguousGeeks.map((name) => `- ${name}`),
      "",
    );
  }
  if (analysis.warnings.length > 0) {
    lines.push(
      "## Warnings",
      "",
      ...analysis.warnings.map((warning) => `- ${warning}`),
      "",
    );
  }
  return lines.join("\n");
}

function renderApply(result: ApplyResult): string {
  const lines = [
    "# BGE geek LinkedIn enrichment — apply result",
    "",
    `- Attempted: ${result.attempted}`,
    `- Updated: ${result.updated}`,
    `- Already current: ${result.unchanged}`,
    `- Skipped: ${result.skipped}`,
    "",
  ];
  if (result.updatedGeeks.length > 0) {
    lines.push(
      "## Updated geeks",
      "",
      ...result.updatedGeeks.map((name) => `- ${name}`),
      "",
    );
  }
  if (result.warnings.length > 0) {
    lines.push(
      "## Warnings",
      "",
      ...result.warnings.map((warning) => `- ${warning}`),
      "",
    );
  }
  return lines.join("\n");
}

/** Report definition attached to the geek link enrichment model. */
export const report = {
  name: "@alvagante/geek-link-enrichment-report",
  description:
    "Review exact, ambiguous, conflicting, and applied geek link matches",
  scope: "method",
  labels: ["bge", "linkedin", "enrichment"],
  execute: async (
    context: ReportContext,
  ): Promise<{ markdown: string; json: Record<string, unknown> }> => {
    if (context.executionStatus === "failed") {
      const json = {
        status: "failed",
        method: context.methodName,
        error: context.errorMessage ?? "Unknown error",
      };
      return {
        markdown: `# BGE geek LinkedIn enrichment\n\nFailed: ${json.error}\n`,
        json,
      };
    }
    if (context.methodName === "analyze") {
      const raw = await readOutput(context, "analysis");
      if (!raw) {
        return {
          markdown:
            "# BGE geek LinkedIn enrichment\n\nNo analysis data produced.\n",
          json: { status: "empty", method: context.methodName },
        };
      }
      const analysis = raw as unknown as Analysis;
      return {
        markdown: renderAnalysis(analysis),
        json: { status: "succeeded", method: context.methodName, ...analysis },
      };
    }
    const raw = await readOutput(context, "applyResult");
    if (!raw) {
      return {
        markdown: "# BGE geek LinkedIn enrichment\n\nNo apply data produced.\n",
        json: { status: "empty", method: context.methodName },
      };
    }
    const result = raw as unknown as ApplyResult;
    return {
      markdown: renderApply(result),
      json: { status: "succeeded", method: context.methodName, ...result },
    };
  },
};
