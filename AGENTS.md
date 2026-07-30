# Repository Guide

## What This Repository Contains

This is the Italian-language website and content pipeline for the **La Brigata dei
Geek Estinti** podcast.

- The main application is a Jekyll 4.3 site. `_episodes/` and `_geeks/` are the
  two output collections; `_layouts/`, `_includes/`, `css/`, and `assets/`
  implement the site.
- `bin/` contains Python and shell utilities for turning recordings and YouTube
  metadata into transcripts, summaries, quotes, articles, covers, and episode
  frontmatter.
- `social-quote-generator/` is a separate installable Python package. Follow its
  more specific `CLAUDE.md` when working in that subtree.

## Content Contracts

- Episode files are named `_episodes/<number>.md`. Preserve the YAML frontmatter
  schema documented in `bin/README_VALIDATOR.md`; the body after the frontmatter
  is rendered as the OpenAI editorial.
- Keep `number` quoted as a string, `duration` as seconds, `youtube` as the
  11-character video ID, and `date` in `YYYY-MM-DD` form. `tags`, `summary`, and
  `guests` are lists. `links` is a label-to-URL mapping when present.
- Guest and host names must exactly match a `_geeks/*.md` file's `nome` value.
  Geek files use `layout: geek` and list episode numbers in `episodi`.
- Preserve Italian copy, accents, names, and existing editorial voice. Avoid
  broad formatting or encoding rewrites in generated episode content.
- `_site/` and `.jekyll-cache/` are generated output; never edit them as source.

## Development and Validation

```bash
# Install Ruby dependencies
bundle install

# Run the site locally with the development URL
bundle exec jekyll serve --livereload --config _config.yml,_config_dev.yml

# Production-style build
bundle exec jekyll build

# Validate one episode, or the full collection
python3 bin/validate_frontmatter.py _episodes/114.md
python3 bin/validate_frontmatter.py _episodes

# Work on the nested Python package
cd social-quote-generator
python -m pip install -e ".[dev]"
pytest
```

Run the narrowest relevant validation after a change. For layout, include, CSS,
config, or collection changes, run a Jekyll build. For episode metadata, run the
frontmatter validator on the changed file. For `social-quote-generator/`, run its
focused test first and then its full pytest suite when practical.

## Operational Safety

- Many `bin/` scripts are batch pipelines, use hard-coded local/OneDrive paths,
  invoke FFmpeg or other system tools, and may overwrite generated content.
  Inspect a script and its arguments before running it; do not run
  `bin/DoEverything.sh` for a routine code or content change.
- LLM/media scripts can use paid external APIs via environment variables such as
  `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `NVIDIA_API_KEY`,
  and `MINAI_API_KEY`. Never commit credentials, `.env` files, or API responses
  containing secrets.
- Social publishing and queue commands can create external posts. Use
  `bge-quote-gen --dry-run` for verification unless the user explicitly asks to
  publish or mutate the queue.

<!-- BEGIN swamp managed section - DO NOT EDIT -->
# Project

This repository is managed with [swamp](https://github.com/swamp-club/swamp).

## Rules

1. **Search before you build.** When automating AWS, APIs, or any external service: (a) search community extensions with `swamp extension search <query>` — prefer `@swamp/*` official extensions first, (b) search local/installed types with `swamp model type search <query>`, (c) if a community extension exists, install it with `swamp extension pull <package>` instead of building from scratch, (d) extend an existing type if it covers the domain but lacks the method you need, (e) only create a custom extension model in `extensions/models/` as a last resort. Read `.agents/skills/swamp/SKILL.md` for guidance. The `command/shell` model is ONLY for ad-hoc one-off shell commands, NEVER for wrapping CLI tools or building integrations.
2. **Extend, don't be clever.** When a model covers the domain but lacks the method you need, extend it with `export const extension` — don't bypass it with shell scripts, CLI tools, or multi-step hacks. One method, one purpose. Use `swamp model type describe <type> --json` to check available methods.
3. **Use the data model.** Once data exists in a model (via `lookup`, `start`, `sync`, etc.), reference it with CEL expressions. Don't re-fetch data that's already available.
4. **CEL expressions everywhere.** Wire models together with CEL expressions. Always prefer `data.latest("<name>", "<dataName>").attributes.<field>` over the deprecated `model.<name>.resource.<spec>.<instance>.attributes.<field>` pattern.
5. **Verify before destructive operations.** Always `swamp model get <name> --json` and verify resource IDs before running delete/stop/destroy methods.
6. **Prefer fan-out methods over loops.** When operating on multiple targets, use a single method that handles all targets internally (factory pattern) rather than looping N separate `swamp model method run` calls against the same model. Multiple parallel calls against the same model contend on the per-model lock, causing timeouts. A single fan-out method acquires the lock once and produces all outputs in one execution. Check `swamp model type describe` for methods that accept filters or produce multiple outputs.
7. **Extension npm deps are bundled, not lockfile-tracked.** Swamp's bundler inlines all npm packages (except zod) into extension bundles at bundle time. `deno.lock` and `package.json` do NOT cover extension model dependencies — this is by design. Always pin explicit versions in `npm:` import specifiers (e.g., `npm:lodash-es@4.17.21`).
8. **Reports for reusable data pipelines.** When the task involves building a repeatable pipeline to transform, aggregate, or analyze model output (security reports, cost analysis, compliance checks, summaries), create a report extension. Read `.agents/skills/swamp/SKILL.md` for guidance.
9. **"Workflow" means a swamp workflow.** In this repository the word "workflow" (and "create/run/execute/validate/debug workflow", "automate", "orchestrate", "automated/nightly job") refers to a swamp workflow — a declarative YAML DAG of model-method steps authored via `swamp workflow create`. Read `.agents/skills/swamp/SKILL.md` for these requests. Do NOT interpret these as a request to build an agent task list, spin up worktrees, or schedule a cron/remote agent. Only use those orchestration mechanisms when the user explicitly names one (e.g. "task list", "subagent", "worktree", "cron", "remote agent") or explicitly asks you to do the work yourself step by step rather than author a swamp workflow.
10. **Use swamp, don't bypass it.** Always work through swamp commands — don't go around them with raw shell tools. Use `swamp data query` to find data, not `grep`/`find` on `.swamp/` files. Use model methods to interact with resources, not `curl`/`aws`/`gcloud`/`kubectl` when a model type already wraps that API — check with `swamp model type search`. Use `swamp help` for CLI discovery, not guesswork. Composing with swamp output is fine (e.g. piping `--json` through `jq`) — the anti-pattern is bypassing swamp entirely.
11. **Inspect reports after failures.** When a model method or workflow run fails, inspect its generated reports before retrying or changing definitions. Reports run even on failure and capture structured diagnostics — error messages, execution status, arguments, and data output pointers. Use `swamp report get @swamp/method-summary --model <model> --json` for method failures or `swamp report get @swamp/workflow-summary --workflow <workflow> --json` for workflow failures. Run `swamp help report get` to confirm current retrieval syntax.

## Skills

**IMPORTANT:** Skills are detailed guides stored in `.agents/skills/`. When a task
matches a skill area below, read the corresponding `SKILL.md` file for guidance.

- `.agents/skills/swamp/SKILL.md` - Swamp CLI — models, workflows, data, vaults, extensions, publishing, repos, reports, issues, and troubleshooting
- `.agents/skills/swamp-getting-started/SKILL.md` - Interactive onboarding for new swamp users

## Getting Started

**IMPORTANT:** At the start of every conversation, run
`swamp model search --json`. If no models are returned (empty result), you MUST
immediately read `.agents/skills/swamp-getting-started/SKILL.md` and follow its
instructions. This walks new users through an interactive onboarding tutorial.

If models already exist, start by reading `.agents/skills/swamp/SKILL.md`
to work with swamp models.

## Commands

Use `swamp --help` to see available commands. For a machine-readable JSON
schema of the CLI (commands, options, arguments) intended for agent
consumption, run `swamp help [<command>...]` — e.g. `swamp help` returns
the full tree, and `swamp help model method run` scopes to a subtree.
<!-- END swamp managed section -->
