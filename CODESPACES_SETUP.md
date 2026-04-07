# Codespaces Setup Guide — PWMP SEO Audit

Step-by-step guide for opening and using the PWMP SEO Audit system in GitHub Codespaces. No local software installation required beyond a web browser.

---

## What is a Codespace?

A Codespace is a cloud computer you access through your browser. When you open the PWMP SEO Audit repo in a Codespace, GitHub spins up a Linux machine with VS Code, Python, and Claude Code already installed. You type commands in the built-in terminal and your audit outputs are saved inside that cloud machine.

---

## One-time setup (do this once per person)

### Step 1 — Get access to the repo

Ask Kaye to invite you as a collaborator on the `pwmp-seo-audit` GitHub repo. You will receive an email invitation — accept it.

### Step 2 — Create your Codespace

1. Go to the repo on GitHub: `https://github.com/<your-org>/pwmp-seo-audit`
2. Click the green **Code** button.
3. Select the **Codespaces** tab.
4. Click **Create codespace on main**.

GitHub will show a spinner for about 1–2 minutes. It is building your cloud machine and installing everything automatically.

When it finishes, a VS Code window opens in your browser.

### Step 3 — Authenticate Claude Code

In the VS Code window, open the terminal:
- Press **Ctrl + \`** (backtick) on Windows/Linux
- Press **Cmd + \`** on Mac
- Or go to the top menu: **Terminal → New Terminal**

Type this command and press Enter:
```
claude auth
```

A browser window will open asking you to log in with your Anthropic account. Log in, then come back to the terminal. You will see a confirmation message.

### Step 4 — Connect Ahrefs

Still in the terminal, type:
```
claude mcp add ahrefs
```

Follow the prompts to connect your Ahrefs account. This is required for real backlink and ranking data in the audit. You only do this once — your Codespace remembers it.

---

## Running an audit

### Every time you want to run an audit

1. Go to `https://github.com/<your-org>/pwmp-seo-audit`
2. Click **Code → Codespaces** — you will see your existing Codespace listed. Click it to reopen it.
3. Open the terminal (Ctrl + \` or Cmd + \`).
4. Type:
   ```
   claude
   ```
   and press Enter. You will see the Claude Code prompt.
5. Type:
   ```
   /audit-client
   ```
   and press Enter.

Claude will ask you for three things:
- The **Typeform CSV** — drag the file into the terminal window, or paste the path.
- The **client's website URL** — paste it.
- The **sales call transcript** — drag the .txt or .pdf file, or paste the transcript text.

Then Claude runs the full 8-step audit automatically. This takes several minutes.

### When the audit finishes

Claude will tell you where the two output files are saved:

```
outputs/<client-slug>/<client-slug>-seo-audit.pdf
outputs/<client-slug>/<client-slug>-website-structure.xlsx
```

To download them to your computer:
1. In the VS Code sidebar, open the **Explorer** panel (file icon on the left).
2. Navigate to `outputs/<client-slug>/`.
3. Right-click the PDF → **Download**.
4. Right-click the XLSX → **Download**.

For the XLSX: drag it into Google Drive and open it with Google Sheets. Then rename it to **"[Business Name] — Website Structure Template"**.

---

## Saving client data between sessions

Codespaces can go to sleep after a period of inactivity, but your files are saved automatically. When you reopen the Codespace, everything is still there.

**Important:** Output files are saved inside your personal Codespace, not shared with teammates. If you want to share an audit, download the files and send them (or put them in the shared Google Drive folder as usual).

---

## Getting updates

When Kaye pushes improvements to the workflow, you get them by pulling in the terminal:

```
git pull origin main
```

---

## Billing

Codespaces is billed per hour of compute time. On the free GitHub plan, you get 60 hours/month. The organization account may have more. Running one audit takes roughly 5–10 minutes of active compute. If you are not running an audit, stop the Codespace to save hours:

1. Go to `https://github.com/codespaces`
2. Find your Codespace and click **Stop codespace**.

---

## Troubleshooting

**"claude: command not found"**
Run `.devcontainer/setup.sh` in the terminal to reinstall. This is rare and usually means the container rebuild was interrupted.

**"Ahrefs MCP not connected"**
Run `claude mcp add ahrefs` again and follow the prompts.

**"PDF not found" from the validator**
The audit didn't finish. Re-run `/audit-client` and check for error messages in the terminal output.

**Codespace won't open**
Go to `https://github.com/codespaces`, delete the stuck Codespace, and create a new one. Your work inside outputs/ will be lost, but the workflow and scripts are all in the repo.
