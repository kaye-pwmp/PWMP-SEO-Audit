# PWMP Logo Placement

The PDF cover page expects a logo at:

```
templates/pdf/assets/pwmp-logo.png
```

**Status:** Placeholder — drop the real logo file here before the first run.

## Expected artwork

Based on the wordmark Kaye provided, the logo is:

- **"Pressure Washing"** — red (#BC0300), italic script
- **"MARKETING PROS"** — navy (#07457C), bold block capitals
- **Water-splash accent** — navy droplets curving up and over the top-right
- Transparent background (PNG with alpha)
- Roughly 2.5:1 aspect ratio (wide wordmark)

The PDF builder renders the logo on the cover page at `2.8" × 1.1"` using `kind="proportional"`, so any reasonable aspect ratio will scale cleanly. A transparent background is strongly preferred so it sits cleanly on the white cover page.

## Preparing the file

1. Save the logo from Kaye's message as a PNG named exactly `pwmp-logo.png`.
2. Place it at `templates/pdf/assets/pwmp-logo.png` (replacing this placeholder file).
3. Commit it to the repo so every teammate gets it on clone.

## Fallback behavior

If the file is missing at render time, `scripts/build_pdf.py` prints a warning and falls back to a text-only cover page. This is intentional so a missing logo never blocks a client audit — but it should not ship this way to clients.
