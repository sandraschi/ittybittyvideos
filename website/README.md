# ittybitty marketing site

Static one-pager for **ittybitty** / ittybittyvideos. No build step.

**Source of truth:** edit files here, then sync to `docs/` for GitHub Pages (see below).

## Preview locally

```powershell
Set-Location D:\Dev\repos\videogen-mcp\website
Start-Process index.html
```

Or serve on a port:

```powershell
Set-Location D:\Dev\repos\videogen-mcp\website
py -m http.server 8080
```

Open http://127.0.0.1:8080/

## GitHub Pages (public repo)

Pages serves from **`/docs`** on `main`:

1. Make repo public (see [docs/ALPHA-RELEASE-CHECKLIST.md](../docs/ALPHA-RELEASE-CHECKLIST.md))
2. Settings → Pages → branch `main`, folder `/docs`
3. Live URL: https://sandraschi.github.io/ittybittyvideos/

Sync after edits:

```powershell
Copy-Item D:\Dev\repos\videogen-mcp\website\index.html D:\Dev\repos\videogen-mcp\docs\index.html -Force
Copy-Item D:\Dev\repos\videogen-mcp\website\style.css D:\Dev\repos\videogen-mcp\docs\style.css -Force
```

`docs/.nojekyll` disables Jekyll so `index.html` is served as pure static HTML alongside technical markdown (linked from README, not rendered on Pages).

## Content

- Alpha banner + hero + three surfaces (Windows / web / MCP)
- Pipeline, R1–R3/R9 features, footage sources
- Links to GitHub **pre-releases** (not `latest` until stable)

For technical docs see `../docs/` (markdown) and the in-app **Help** page.
