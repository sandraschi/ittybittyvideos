# ittybitty — TODO (agent tracker)

**Product:** ittybitty · **Repo folder:** `videogen-mcp` · **Version:** 0.2.0  
**Assessment:** [ASSESSMENT.md](./ASSESSMENT.md) · **Gitignore:** [docs/GITIGNORE-ASSESSMENT.md](./docs/GITIGNORE-ASSESSMENT.md) · **Roadmap:** [SPEC.md](./SPEC.md)

---

## At a glance

| Priority | Item | Status |
|----------|------|--------|
| P0 | Free stock parity (Pexels + Pixabay + Coverr) | ✅ 2026-06-14 |
| P0 | Free stock beyond MPT (Mixkit + NASA, no key) | ✅ 2026-06-14 |
| P0 | Rebuild NSIS installer post-rebrand | ✅ 2026-06-14 → `dist/ittybitty-0.2.0-x64-setup.exe` (33.2 MB) |
| P0 | GSD puppy demo (poster + optional release MP4) | ⬜ script: `render_gsd_demo.ps1` |
| P1 | Upload fresh NSIS to GitHub Release `v0.2.0` | ⬜ after local build |
| P1 | YouTube Shorts upload API (Publish Tier 2) | ⬜ |
| P1 | FFmpeg compose integration test (mocked) | ⬜ |
| P1 | R3 critique report on job detail page | ⬜ |
| P2 | mcpb packaging | ⬜ deferred |
| P2 | MCD project page version → 0.2.0 sync | ⬜ |
| P2 | Multi-provider stock fallback (Pexels→Pixabay→Coverr) | ⬜ |

---

## Shipped (0.2.0+) — do not re-open

- ✅ SQLite job store + depot UI
- ✅ Webapp (15 pages) + Settings + Help + Logs + Addons
- ✅ MCP catalog (16 tools) + `videogen_help` first
- ✅ Director UX (8 recipes, length on Generate default path)
- ✅ Jellyfin / Plex / Google Veo·Omni / LocalGen stock
- ✅ **Free stock APIs:** Pexels, Pixabay, Coverr (MPT parity)
- ✅ R1 alignment, R2 beat snap, R3 screening (live-validated run `a9e798ffba86`)
- ✅ R10 prompt director + trope templates
- ✅ Silent B-roll A/V drift fix (`cb2c701`)
- ✅ Addon module download system (`647c485`)
- ✅ Windows NSIS + Tauri (backend spawn fix)
- ✅ Fleet dev launch (:11055 + :11054)
- ✅ Rebrand to **ittybitty**
- ✅ **193+ tests**, ruff clean

---

## P0 — Next sessions

### Native release

- [x] `native/build.ps1` → `dist/ittybitty-0.2.0-x64-setup.exe` (2026-06-14)
- [ ] Smoke: installed app → `/health` OK, `tool_count` = 16
- [ ] `gh release upload` (replace stale 2026-06-12 asset)

### Demo asset (GSD puppy)

- [ ] Render ~20 s vertical short (`scripts/render_gsd_demo.ps1`, trope `pet-food-duo-review`)
- [ ] Poster JPG → `docs/examples/gsd-puppy-poster.jpg`
- [ ] README link (image only; MP4 on release, not git)

### R9 talking-head overlay

- [x] TalkerProvider ABC + sadtalker HTTP + pipeline post-pass
- [ ] Backend wrapper (SadTalker/LivePortrait on Goliath :11100)
- [ ] Webapp Settings: talker section
- [ ] Real render validation

---

## P1 — Quality & publish

- [ ] Mocked FFmpeg test for `compose.py` argv
- [ ] Publish Tier 2: YouTube Data API resumable Shorts upload
- [ ] Apply [gitignore assessment](./docs/GITIGNORE-ASSESSMENT.md) MP4 policy
- [ ] VLM default → `gemma4:12b` when pulled (e4b validated; 26b won't fit 4090)

---

## P2 — Fleet & packaging

- [ ] `.mcpb` build + INSTALL Option B
- [ ] Update `mcp-central-docs/projects/ittybitty/README.md` to 0.2.0
- [ ] Hybrid stock fallback chain (one job tries multiple free APIs)

---

## Validation notes (Fable 5 session, harness only)

Named **`scripts/validate_fable.py`** after the Anthropic review agent — **not** a video provider.

- [x] R1/R2/R3 live end-to-end (2026-06-13)
- [x] Empty-narration drift mitigated in compose (`cb2c701`); spot-check long jobs
- [ ] Transient ffmpeg under load — stderr in `*.ffmpeg-error.log`

---

## Agent instructions

1. Pick one P0/P1 row; finish before new SPEC phases.  
2. Update this file when closing items.  
3. Do not commit `.env`, `output/`, or `native/resources/*.exe`.
