# Handover Document for Claude (`videogen-mcp` / `ittybitty`)

**Repository:** `videogen-mcp` (`ittybitty`)
**Last Updated:** 2026-08-21
**Status:** Operational (v0.3.0) · LocalGen Studio + Meituan LongCat-Video 13.6B Engine · 100% Test Pass Rate

---

## 1. System Architecture & Ports

| Component | Port / Scheme | Description |
|---|---|---|
| **LocalGen Sidecar** | `http://localhost:8188` | Local AI Video Generation engine (`localgen_server.app`) |
| **FastMCP Backend** | `http://localhost:11054` | FastMCP 3.4+ portmanteau tool server |
| **SOTA Web Dashboard** | `http://localhost:11055` | Vite + React + Tailwind dashboard (`webapp`) |

---

## 2. Core Capabilities & Recent Accomplishments (v0.3.0)

1. **Meituan LongCat-Video 13.6B DiT Integration:**
   - **Backend Loader:** Registered `longcat-video-13b` (`meituan-longcat/LongCat-Video`) in [`backends/__init__.py`](../src/videogen_mcp/localgen_server/backends/__init__.py) with CUDA memory offloading (`_load_longcat()` in [`loader.py`](../src/videogen_mcp/localgen_server/backends/loader.py)).
   - **Video Continuation API:** Exposed REST endpoint `POST /api/extend` in [`app.py`](../src/videogen_mcp/localgen_server/app.py) for native minute-long video continuation.

2. **LocalGen Studio Web Interface (`webapp/src/pages/localgen.tsx`):**
   - Built LocalGen Studio (`/localgen`) with live sidecar telemetry, engine selector cards, T2V/continuation tabbed workflow, frame/guidance sliders, and HTML5 MP4 player export.
   - Updated sidebar navigation in [`Sidebar.tsx`](../webapp/src/components/layout/Sidebar.tsx) and in-app help panel [`help.tsx`](../webapp/src/pages/help.tsx).

3. **Product Requirements & Specifications:**
   - Authored PRD [`PRD.md`](../PRD.md) (v0.3.0), updated [`SPEC.md`](../SPEC.md), [`README.md`](../README.md), and [`CHANGELOG.md`](../CHANGELOG.md).

---

## 3. FastMCP Tool Surface

FastMCP tools are consolidated into operation-based portmanteau tools:
- `videogen_render`: Video rendering, chapter assembly, and clip stitching.
- `videogen_stock`: B-roll stock footage retrieval and local media library search.
- `videogen_pipeline`: Full script-to-video workflow orchestration.

---

## 4. Verification Commands

```powershell
# Run videogen-mcp Python test suite
uv run pytest tests/test_localgen_longcat.py -q

# Run webapp TypeScript check
npx tsc --noEmit (in webapp)
```

---

*Handover document prepared by Antigravity AI Orchestrator · 2026*
