# PWMP SEO Audit — Claude Code Project Guide

You are Claude Code running inside the **pwmp-seo-audit** project for Pressure Washing Marketing Pros (PWMP). This file is your standing orders for every session.

## What this project does

Given three inputs about a PWMP client — a Typeform CSV, a live website URL, and a sales-call transcript — produce two deliverables:

1. `outputs/<client-slug>/<client-slug>-seo-audit.pdf` — 12-section branded audit
2. `outputs/<client-slug>/<client-slug>-website-structure.xlsx` — 8-tab website structure template

## How to run the workflow

The user will typically trigger the workflow with the `/audit-client` slash command (see `.claude/commands/audit-client.md`). When that happens:

1. Load the `seo-audit-report` skill at `.claude/skills/seo-audit-report/SKILL.md`.
2. Follow its 8 steps exactly.
3. Use `scripts/build_pdf.py` to generate the PDF — do not hand-roll a PDF.
4. Use `scripts/build_sheet.py` to generate the `.xlsx` — do not hand-roll a spreadsheet.
5. After generation, run `scripts/validate_output.py <client-slug>` and only declare success if it passes.

## Hard rules

- **Source of truth** — transcript wins for strategy (primary city, keyword focus, services to prioritize). Typeform wins for facts (business name, phone, addresses, services offered, competitors, About Us). Every conflict MUST be flagged in the PDF. Full rules: `.claude/skills/seo-audit-report/references/source-of-truth-rules.md`.
- **Brand colors** — `#07457C` (navy) for headings, `#BC0300` (red) for callouts and conflict flags. These are constants in `scripts/build_pdf.py`; don't override.
- **Ahrefs data must be real** — pulled via the Ahrefs MCP. If the Ahrefs MCP is not connected, STOP and tell the user to connect it before continuing. Do not fabricate or estimate backlink/ranking numbers.
- **Services** — only include services that are actually checked on the client's Typeform in the Residential and Commercial sheet tabs and in Section 11 of the PDF.
- **Client data is private** — `outputs/` is gitignored. Never commit client data, never log client PII to stdout outside the session.

## Where things live

| Thing | Path |
|---|---|
| The skill (workflow brain) | `.claude/skills/seo-audit-report/SKILL.md` |
| Detailed rules & references | `.claude/skills/seo-audit-report/references/` |
| PDF generator | `scripts/build_pdf.py` |
| XLSX generator | `scripts/build_sheet.py` |
| Output validator | `scripts/validate_output.py` |
| Brand logo | `templates/pdf/assets/pwmp-logo.png` |
| Per-client deliverables | `outputs/<client-slug>/` |

## When in doubt

Read the references in `.claude/skills/seo-audit-report/references/` before inventing an answer. The agency has strong opinions baked into those files — follow them.
