# ittybitty — TODO (agent tracker)

**Product:** ittybitty · **Repo folder:** `videogen-mcp` · **Version:** 0.2.0  
**Assessment:** [ASSESSMENT-BY-CURSOR.md](./ASSESSMENT-BY-CURSOR.md) · **Gitignore:** [docs/GITIGNORE-ASSESSMENT.md](./docs/GITIGNORE-ASSESSMENT.md) · **Roadmap:** [SPEC.md](./SPEC.md)

---

## At a glance

| Priority | Item | Status |
|----------|------|--------|
| P0 | Wire R2 beat snap (`audio.py` → pipeline) | ⬜ |
| P0 | Rebuild NSIS installer post-rebrand (`ittybitty-*` binaries) | ⬜ |
| P0 | GSD puppy demo (poster in README; MP4 via release or gitignored) | ⬜ |
| P1 | YouTube Shorts upload API (Publish Tier 2) | ⬜ |
| P1 | Gitignore / untrack legacy `docs/examples/*.mp4` | ⬜ |
| P1 | FFmpeg compose integration test (mocked) | ⬜ |
| P2 | mcpb packaging | ⬜ deferred |
| P2 | MCD project page version → 0.2.0 sync | ⬜ |

---

## P0 — Next sessions

### R2 beat-aware cuts (finish Fable slice)

- [ ] Add `beats = ["librosa>=0.10"]` to `pyproject.toml`
- [ ] Import `detect_beats` / `snap_cut_durations` from `services/audio.py` in `pipeline.py` / `pipeline_extended.py` when BGM present
- [ ] Env: `VIDEOGEN_BEAT_SNAP`, `VIDEOGEN_DUCK_DB` (see SPEC)
- [ ] Add `tests/test_audio.py`
- [ ] Commit: `feat(R2): beat snap + music ducking wiring`

### Demo asset (GSD puppy)

- [ ] Render ~20 s vertical short (Jellyfin/Plex or Pexels)
- [ ] Export poster JPG → `docs/examples/gsd-puppy-poster.jpg`
- [ ] Link from README (image only, no `<video>` embed)
- [ ] Optional: attach MP4 to GitHub Release, not git

### Native release

- [ ] `just build-native`
- [ ] Smoke: installed app → `/health` OK
- [ ] `gh release upload` new `ittybitty-0.2.0-x64-setup.exe`

---

## P1 — Quality & publish

- [ ] Mocked FFmpeg test for `compose.py` argv
- [ ] `pyright` clean run documented in assessment
- [ ] Publish Tier 2: YouTube Data API resumable Shorts upload
- [ ] Apply [gitignore assessment](./docs/GITIGNORE-ASSESSMENT.md) MP4 policy

---

## P2 — Fleet & packaging

- [ ] `.mcpb` build + INSTALL Option B
- [ ] Update `mcp-central-docs/projects/ittybitty/README.md` status to 0.2.0
- [ ] Apps Hub / skills provider (deferred)

---

## Shipped (0.2.0) — do not re-open

- ✅ SQLite job store + depot UI
- ✅ SOTA webapp (13 pages) + Settings + Help + Logs
- ✅ Publish handoff API
- ✅ Jellyfin / Plex library stock providers
- ✅ Google Veo / Omni stock layer
- ✅ Windows NSIS + Tauri (backend spawn fix)
- ✅ Fleet-standard dev launch (:11055 + :11054)
- ✅ Rebrand to **ittybitty**
- ✅ 113 tests, ruff clean

---

## Agent instructions

1. Pick one P0 row; finish before starting new SPEC phases (R3+).  
2. Update this file and the assessment agent log when closing items.  
3. Do not commit `.env`, `output/`, or `native/resources/*.exe`.
