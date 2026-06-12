# ittybitty — TODO (agent tracker)

**Product:** ittybitty · **Repo folder:** `videogen-mcp` · **Version:** 0.2.0  
**Assessment:** [ASSESSMENT-BY-CURSOR.md](./ASSESSMENT-BY-CURSOR.md) · **Gitignore:** [docs/GITIGNORE-ASSESSMENT.md](./docs/GITIGNORE-ASSESSMENT.md) · **Roadmap:** [SPEC.md](./SPEC.md)

---

## At a glance

| Priority | Item | Status |
|----------|------|--------|
| P0 | Wire R2 beat snap (`audio.py` → pipeline) | ✅ 2026-06-12 (Fable) |
| P0 | Rebuild NSIS installer post-rebrand (`ittybitty-*` binaries) | ⬜ |
| P0 | GSD puppy demo (poster in README; MP4 via release or gitignored) | ⬜ use trope:pet-food-duo-review |
| P1 | YouTube Shorts upload API (Publish Tier 2) | ⬜ |
| P1 | Gitignore / untrack legacy `docs/examples/*.mp4` | ⬜ |
| P1 | FFmpeg compose integration test (mocked) | ⬜ |
| P2 | mcpb packaging | ⬜ deferred |
| P2 | **R10** Prompt director (trope/genre templates) | ⬜ planned |
| P2 | MCD project page version → 0.2.0 sync | ⬜ |

---

## P0 — Next sessions

### R2 beat-aware cuts — DONE 2026-06-12 (Fable)

- [x] `beats = ["librosa>=0.10"]` in `pyproject.toml`
- [x] `detect_beats` / `snap_cut_durations` wired in `pipeline.py` (extended pipeline has no BGM input yet — nothing to wire)
- [x] Env: `VIDEOGEN_BEAT_SNAP`, `VIDEOGEN_DUCK_RATIO` (DUCK_DB was wrong — no dB knob in sidechaincompress; SPEC corrected)
- [x] `tests/test_audio.py` (18 tests, also covers R9)
- [x] Committed

### R9 talking-head overlay — plumbing DONE 2026-06-12 (Fable)

- [x] TalkerProvider ABC + sadtalker HTTP provider + registry
- [x] `services/overlay.py` scale2ref PiP + pipeline post-pass (failure-safe)
- [ ] Backend wrapper service (FastAPI around SadTalker/LivePortrait on Goliath, port 11100)
- [ ] Webapp Settings: talker section
- [ ] Real render validation (Benny pic + LivePortrait animals mode = demo gold)

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

### R10 Prompt director — trope & genre templates (SPEC Phase 3)

Narrative structure presets before LLM calls. See [SPEC.md § R10](./SPEC.md#phase-3--from-generator-to-tool-v04-4-days).

- [ ] Schema + `templates/tropes/*.yaml` (8 viral exemplars — see EXEMPLARS-RESEARCH.md)
- [ ] `services/prompt_director.py` — `enrich(system, user, structure_id) -> messages`
- [ ] Wire into `generate_script` + `plan_video` when `structure` set
- [ ] `PlanRequest` + REST/MCP optional `structure` param; `videogen_structures` list tool
- [x] Exemplar research doc + trope YAML seeds (`docs/EXEMPLARS-RESEARCH.md`, `templates/tropes/*.yaml`)
- [x] Prompt library exemplar presets + GSD food duo sample
- [x] Docs: `docs/PROMPT-DIRECTOR.md` — mermaid diagrams; no live TVTropes scraping

**Out of scope for v1:** automated trope fetch/scrape; LLM free-form trope invention without template guardrails.

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

### R3 Screening Room - DONE 2026-06-12 (Fable)

- [x] critic.py + critique models + screening loop in pipeline_extended
- [x] videogen_review tool (tool_count 7) + 14 tests (145 total)
- [ ] Live VLM validation: ollama pull a qwen-vl vision model, run one plan_render with VIDEOGEN_SCREENING_PASSES=1, check critique_pass_1.json
- [ ] Webapp: surface critique report on job detail page
