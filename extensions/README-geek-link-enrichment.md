# LinkedIn geek-link enrichment

This swamp pipeline reads an official LinkedIn connections export, matches contacts to `_geeks/*.md` by exact normalized full name, produces a review report, pauses for approval, and then adds safe LinkedIn URLs to frontmatter.

## Expected CSV

The export must contain first-name and last-name columns. The model recognizes common English and Italian headers. A profile URL column is also required to produce candidates; common `URL`, `LinkedIn`, and `Profile URL` variants are detected automatically. If LinkedIn omits profile URLs from the export, the analysis still runs but cannot invent or scrape them.

Only the source filename, column names, public geek names, and public LinkedIn profile URLs are persisted. Email addresses, employers, positions, and the raw CSV are not stored in swamp data.

## Run when the CSV arrives

Use an absolute path to keep the personal export outside the repository:

```sh
swamp workflow run enrich-geek-linkedin \
  --input csvPath=/absolute/path/to/Connections.csv \
  --json
```

If automatic URL-column detection fails, name the header explicitly:

```sh
swamp workflow run enrich-geek-linkedin \
  --input csvPath=/absolute/path/to/Connections.csv \
  --input 'urlColumn=Profile URL' \
  --json
```

For a one-person canary, provide the geek's exact `nome` value:

```sh
swamp workflow run enrich-geek-linkedin \
  --input csvPath=/absolute/path/to/Connections.csv \
  --input 'geekName=Marco Guardigli' \
  --json
```

The workflow stops at `approve-linkedin-links`. Review the generated report before proceeding:

```sh
swamp report get @alvagante/geek-link-enrichment-report \
  --model geek-link-enricher \
  --json
```

Copy the workflow run ID from the run output, then approve and resume that exact run:

```sh
swamp workflow approve enrich-geek-linkedin approve-linkedin-links \
  --run RUN_ID \
  --reason 'Reviewed exact LinkedIn matches' \
  --json

swamp workflow resume enrich-geek-linkedin \
  --run RUN_ID \
  --json
```

After completion, inspect the latest apply report with the same `swamp report get` command and review `git diff -- _geeks` before committing.

## Safety behavior

- Only one-to-one exact normalized full-name matches become candidates.
- Ambiguous names, missing/invalid URLs, and differing existing links are reported but not applied.
- Existing LinkedIn links are never overwritten.
- Each file is hashed during analysis; a file changed before approval is skipped.
- Updates are atomic and fan out within one model-method execution.
- Re-running an approved candidate already applied is an unchanged no-op.
