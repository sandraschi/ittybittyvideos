# ittybitty — TODO (agent tracker)

**Product:** ittybitty · **Repo folder:** `videogen-mcp` · **Version:** 0.2.0  
**Assessment:** [ASSESSMENT.md](./ASSESSMENT.md) · **Roadmap:** [SPEC.md](./SPEC.md)

---

## At a glance

| Priority | Item | Status |
|----------|------|--------|
| P0 | Free stock (Pexels + Pixabay + Coverr + Mixkit + NASA) | ✅ |
| P0 | NSIS rebuild + GitHub Release `v0.2.0` artifact | ✅ |
| P0 | CUA-NSIS 11-phase smoke (local) | ✅ 2026-06-14 |
| P0 | MCPB packaging scaffold | ✅ 2026-06-14 |
| P0 | GSD puppy demo (poster + release MP4) | ⬜ `scripts/render_gsd_demo.ps1` |
| P1 | Installed-app smoke (`/health`, `tool_count`=16) | ⬜ |
| P1 | YouTube Shorts upload (Publish Tier 2) | ⬜ |
| P1 | R3 critique report on job detail page | ⬜ |
| P1 | FFmpeg compose integration test (mocked) | ⬜ |
| P2 | Topic packs (SpaceX, robotics search presets) | ⬜ |
| P2 | Chinese B-roll (Bilibili/Douyin/XHS scrapers) | ⬜ deferred — ToS/maintenance |
| P2 | Multi-provider stock fallback per scene | ⬜ |
| P2 | MCD project page → 0.2.0 sync | ⬜ |
| P2 | Depot as stock source | ⬜ |

---

## Shipped (0.2.0+)

- ✅ 11 stock providers (MPT parity + Mixkit/NASA + library/AI)
- ✅ MCP 16 tools + `videogen_help`
- ✅ Webapp 15 pages, Director UX, Addons
- ✅ R1/R2/R3 + R10 prompt director (live-validated)
- ✅ Windows NSIS + Tauri (CORS `tauri://localhost`)
- ✅ Release notes + `ittybitty-0.2.0-x64-setup.exe` on GitHub
- ✅ **197 tests**
- ✅ MCPB layout + `just mcpb-pack`
- ✅ CUA-NSIS smoke harness + `just cua-nsis-test`

---

## P0 — Next

### GSD demo

- [ ] Render ~20 s vertical (`trope:pet-food-duo-review`)
- [ ] Poster → `docs/examples/gsd-puppy-poster.jpg`
- [ ] Optional MP4 on release only

### Native QA

- [ ] Fresh install smoke: `/health`, 16 MCP tools
- [ ] Re-run CUA-NSIS after next NSIS rebuild

---

## P1 — Quality & publish

- [ ] Mocked FFmpeg compose test
- [ ] YouTube Data API Shorts upload
- [ ] VLM default → `gemma4:12b` when pulled
- [ ] R9 talker backend (:11100) + Settings UI

---

## P2 — Fleet

- [ ] Topic packs: SpaceX (NASA-boosted queries), robotics (stock keywords)
- [ ] Hybrid stock fallback chain
- [ ] `mcp-central-docs/projects/ittybitty` sync
- [ ] Bilibili/Douyin/XHS scrapers (MPT parity — legal review first)

---

## Agent instructions

1. Pick one P0/P1 row before new SPEC phases.
2. Update this file when closing items.
3. Do not commit `.env`, `output/`, `dist/`, `cua-reports/`, `*.log`, `native/resources/*.exe`.
