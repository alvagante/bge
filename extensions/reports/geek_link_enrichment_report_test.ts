import { report } from "./geek_link_enrichment_report.ts";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

Deno.test("analysis report renders review candidates", async () => {
  const payload = {
    csvFileName: "Connections.csv",
    headerRow: 2,
    columns: {
      firstName: "First Name",
      lastName: "Last Name",
      linkedInUrl: "URL",
    },
    counts: {
      geekFiles: 179,
      connectionRows: 500,
      exactCandidates: 1,
      alreadyCurrent: 0,
      conflicts: 0,
      ambiguous: 0,
      unmatchedGeeks: 178,
      matchedWithoutUrl: 0,
      invalidUrls: 0,
    },
    candidates: [{
      geekName: "Marco Guardigli",
      geekFile: "_geeks/Marco Guardigli.md",
      linkedInUrl: "https://www.linkedin.com/in/marcoguardigli/",
      sourceRow: 10,
    }],
    conflicts: [],
    ambiguousGeeks: [],
    unmatchedGeeks: [],
    warnings: [],
  };
  const result = await report.execute({
    modelType: "@alvagante/geek-link-enricher",
    modelId: "test",
    methodName: "analyze",
    executionStatus: "succeeded",
    dataHandles: [{
      name: "analysis-current",
      specName: "analysis",
      version: 1,
    }],
    dataRepository: {
      getContent: () =>
        Promise.resolve(new TextEncoder().encode(JSON.stringify(payload))),
    },
  });
  assert(result.markdown.includes("Marco Guardigli"), "candidate missing");
  assert(result.markdown.includes("Exact candidates | 1"), "count missing");
});
