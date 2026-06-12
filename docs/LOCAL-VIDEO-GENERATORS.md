# Local AI video generators — fleet externals & ittybitty

How **Wan**, **Hunyuan WorldPlay**, and the built-in **LocalGen sidecar** relate to ittybitty stock footage.

---

## Quick answer

| Source | Path | In ittybitty today? | Role |
|--------|------|---------------------|------|
| **LocalGen sidecar** (built-in) | `videogen-mcp` → `localgen_server/` | **Yes** — `VIDEOGEN_STOCK_PROVIDER=localgen` | HTTP `:8188`, Diffusers Wan 2.2 weights |
| **wan-video** (fleet external) | `D:\Dev\repos\externals\wan-video` | **Not wired** — same model family, richer CLI | Native Wan 2.2 (T2V, I2V, S2V, Animate); optional MCP |
| **hunyuan-worldplay** (fleet external) | `D:\Dev\repos\externals\hunyuan-worldplay` | **Not wired** — roadmap | Interactive world streaming (HY-World 1.5 / WorldPlay) |

Pexels / Jellyfin / Plex / Google Veo are separate stock paths — see [EXTERNAL-REFERENCES.md](./EXTERNAL-REFERENCES.md).

---

## What is already integrated: LocalGen (`localgen`)

ittybitty ships an HTTP sidecar that the stock provider `localgen` (alias `cogvideo`) calls:

```
POST http://127.0.0.1:8188/api/generate
  { "prompt": "...", "aspect": "9:16" }
  → MP4 clip bytes
```

**Start:**

```powershell
Set-Location D:\Dev\repos\videogen-mcp
pip install -e ".[localgen]"
.\start-localgen.bat
# or: .\scripts\start_localgen.ps1
```

**Settings:** `VIDEOGEN_STOCK_PROVIDER=localgen`, `LOCALGEN_URL=http://127.0.0.1:8188`, `LOCALGEN_BACKEND=wan22-14b` or `wan22-5b`.

**Backends** (`src/videogen_mcp/localgen_server/backends/__init__.py`):

| `LOCALGEN_BACKEND` | Hugging Face model | VRAM hint |
|--------------------|-------------------|-----------|
| `wan22-14b` (default) | `Wan-AI/Wan2.2-T2V-A14B-Diffusers` | ~24 GB class |
| `wan22-5b` | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | 4090-friendly, 720p@24fps |
| `cogvideo-2b` | `THUDM/CogVideoX-2b` | Legacy |

This uses **Diffusers** pipelines inside the repo — not the external `wan-video` tree.

---

## Fleet external: `externals/wan-video`

**Path:** `D:\Dev\repos\externals\wan-video`  
**Upstream:** [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) (Apache 2.0)

Sandra’s fleet clone adds MCP/uv packaging (`start.ps1` → `uv run -m wan`). It exposes the **full upstream surface**:

- T2V / I2V / TI2V (5B & A14B MoE)
- **S2V** — speech-to-video (pairs with narration / CosyVoice)
- **Animate** — character animation & replacement

**Not yet** exposed as `LOCALGEN_URL` to ittybitty. Integration options (future):

1. Thin HTTP wrapper in `wan-video` implementing the same contract as LocalGen (`POST /api/generate`).
2. New stock provider key `wan-native` pointing at that wrapper.
3. Use S2V/Animate for R9-adjacent workflows (talking pets, character B-roll).

**Run standalone:**

```powershell
Set-Location D:\Dev\repos\externals\wan-video
.\start.ps1
```

See that repo’s [README](file:///D:/Dev/repos/externals/wan-video/README.md) for model downloads (Hugging Face / ModelScope).

---

## Fleet external: `externals/hunyuan-worldplay`

**Path:** `D:\Dev\repos\externals\hunyuan-worldplay`  
**Upstream:** Tencent **HY-World 1.5 (WorldPlay)** — [project page](https://3d-models.hunyuan.tencent.com/world/) · [Hugging Face](https://huggingface.co/tencent/HY-WorldPlay) · [paper](https://arxiv.org/abs/2512.14614)

Interactive **streaming world** model (keyboard/mouse actions, 24 FPS chunks, long-horizon consistency). Includes:

- **WorldPlay-8B** (Hunyuan Video lineage)
- **WorldPlay-5B** (Wan-based, lower VRAM)

**Not integrated** with ittybitty’s scene-based B-roll pipeline today. Different product shape: exploratory worlds vs per-scene stock clips.

**Plausible fleet fit (roadmap):**

- Long-take B-roll or “fly through Vienna” segments fed into compose
- Hybrid: WorldPlay chunk → trim → depot clip (like Jellyfin library trims)
- Requires a sidecar + stock provider (same pattern as LocalGen)

**Run standalone:** follow `externals/hunyuan-worldplay/README.md` (conda env `worldplay`, heavy GPU).

---

## Comparison

| | LocalGen (in repo) | wan-video external | hunyuan-worldplay |
|--|-------------------|-------------------|-------------------|
| **ittybitty stock key** | `localgen` | — | — |
| **Port** | 8188 | (MCP / CLI) | (inference scripts) |
| **Best for** | Per-scene T2V B-roll in Short/Mid pipeline | Full Wan suite, S2V, Animate, research | Interactive worlds, camera control |
| **VRAM** | 5B–14B Diffusers | 24–80+ GB depending on task | 28–72 GB (see their README) |
| **License** | Wan weights: Apache 2.0 | Apache 2.0 | Check Tencent / HF model card |

---

## Related docs

- [CONFIGURATION.md](./CONFIGURATION.md) — `LOCALGEN_*` env vars  
- [EXTERNAL-REFERENCES.md](./EXTERNAL-REFERENCES.md) — official Wan / Hugging Face links  
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) — LocalGen OOM, health checks  
- Marketing overview: [website/index.html](../website/index.html)
