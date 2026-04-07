# PWMP SEO Audit — Claude Code Project

An automated SEO & Local Visibility Audit system for **Pressure Washing Marketing Pros (PWMP)**, built to run inside [Claude Code](https://docs.claude.com/en/docs/claude-code/overview).

Given a client's Typeform CSV, their website URL, and a sales-call transcript, Claude Code will produce:

1. A branded **PDF audit report** (12 sections, PWMP brand colors, ReportLab-generated).
2. A **website structure `.xlsx`** with 8 pre-populated tabs, ready to upload into Google Drive as a Google Sheet.

## Running in GitHub Codespaces (recommended for teams)

No local install needed. Every teammate runs the system in a cloud VS Code environment directly from the browser.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/<YOUR-ORG>/pwmp-seo-audit)

> Replace `<YOUR-ORG>` in the badge URL above with your GitHub org/username after you push the repo.

**First time only (per teammate):**
1. Click the badge above (or go to the repo on GitHub → green **Code** button → **Codespaces** tab → **Create codespace on main**).
2. Wait ~2 minutes for the container to build. Python deps and Claude Code CLI install automatically.
3. In the VS Code terminal that opens, run:
   ```
   claude auth
   ```
   and authenticate with your Anthropic account.
4. Connect the Ahrefs MCP (required for live data):
   ```
   claude mcp add ahrefs
   ```
5. Done. Run audits with:
   ```
   claude
   /audit-client
   ```

**Every subsequent audit:**
Just reopen the Codespace (it stays alive) and run `claude` → `/audit-client`.

For the full step-by-step guide with screenshots, see [CODESPACES_SETUP.md](CODESPACES_SETUP.md).

---

## Local installation (alternative)

### Requirements

- Python 3.10+
- [Claude Code CLI](https://docs.claude.com/en/docs/claude-code/overview) installed and authenticated
- Ahrefs MCP connector configured in Claude Code for live backlink/ranking data
- PWMP logo at `templates/pdf/assets/pwmp-logo.png` (replace the placeholder before first run)

```bash
git clone <this-repo-url> pwmp-seo-audit
cd pwmp-seo-audit
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Drop the real PWMP logo into `templates/pdf/assets/pwmp-logo.png`.

## Usage

From inside the project directory, start Claude Code and run the slash command:

```
claude
> /audit-client
```

Claude will ask for the three inputs (Typeform CSV, website URL, transcript), run the full 8-step workflow described in `.claude/skills/seo-audit-report/SKILL.md`, and save deliverables to:

```
outputs/<client-slug>/
  ├── <client-slug>-seo-audit.pdf
  └── <client-slug>-website-structure.xlsx
```

After the run, upload the `.xlsx` into Google Drive and open it as a Google Sheet — the 8 tabs carry over cleanly.

## Project layout

```
pwmp-seo-audit/
├── README.md                          # this file
├── CLAUDE.md                          # project guide loaded by Claude Code on every session
├── .claude/
│   ├── commands/
│   │   └── audit-client.md            # /audit-client slash command
│   └── skills/
│       └── seo-audit-report/
│           ├── SKILL.md               # lean entry point, links to references
│           └── references/
│               ├── source-of-truth-rules.md
│               ├── pdf-report-structure.md
│               ├── sheet-template-spec.md
│               ├── ahrefs-mcp-guide.md
│               └── google-sheets-upload-guide.md
├── templates/
│   ├── pdf/assets/pwmp-logo.png       # REPLACE with real logo
│   └── sheet/                         # reserved for future master template
├── scripts/
│   ├── build_pdf.py                   # ReportLab PDF generator
│   ├── build_sheet.py                 # openpyxl 8-tab xlsx generator
│   └── validate_output.py             # pre-delivery checklist automation
├── outputs/                           # per-client deliverables land here
├── requirements.txt
└── .gitignore
```

## Updating the workflow

All agency logic lives in `.claude/skills/seo-audit-report/`. To change brand colors, sections, or rules, edit `SKILL.md` or the `references/` files — no code changes needed.

Branding scripts (`build_pdf.py`, `build_sheet.py`) only change if the *structure* of deliverables changes.

## Team workflow

1. Clone the repo to your machine.
2. Connect your Ahrefs MCP in Claude Code (once).
3. Run `/audit-client` per client — all client data stays on your machine and in `outputs/`.
4. Never commit client data — `outputs/` is gitignored.

---

*Maintained by Pressure Washing Marketing Pros.*
