# Product Requirements Document (PRD): ittybitty (`videogen-mcp`)

**Product Name:** ittybitty
**Repository:** `sandraschi/ittybittyvideos` (`videogen-mcp`)
**Target Version:** 0.3.0
**Backend Port:** 11054 | **Webapp Port:** 11055 | **LocalGen Sidecar Port:** 8188

---

## 1. Executive Summary & Vision

`ittybitty` is the fleet-grade open-source AI video generation system. It bridges high-level topic planning, custom script narration, stock library retrieval (Pexels, Mixkit, NASA, Jellyfin/Plex), and local open-weight AI video diffusion engines (**Meituan LongCat-Video 13.6B DiT**, **Wan 2.2 14B/5B**, **CogVideoX 2B**) into a single unified workspace.

---

## 2. Core Personas & Usage Modes

1. **Standalone Windows Desktop User:** Single NSIS installer bundling PyInstaller backend and React webapp.
2. **Web Dashboard Contributor / Power User:** React + Vite + Tailwind dashboard (`http://localhost:11055`) with dedicated studios for Short Video, Mid-Length Planning, LocalGen Studio, Depot asset management, and Publish handoff.
3. **AI Agent / Fleet Automation Client:** FastMCP 3.2 protocol endpoint (`/mcp` on port 11054) allowing Claude Code, Cursor, and OpenClaw agents to invoke 16+ video orchestration tools.

---

## 3. Product Capabilities & Tiers

### 3.1 Local Generative AI Video (`localgen_server`)
* **Meituan LongCat-Video (13.6B Dense DiT):** 720p @ 30 FPS. Pretrained on native **Video Continuation** for minute-long video synthesis without quality degradation or color drift.
* **Wan 2.2 (14B T2V / 5B TI2V):** High-definition diffusion text & image-to-video generation.
* **CogVideoX (2B):** Lightweight legacy fallback.

### 3.2 Web Interface (`LocalGen Studio`)
* **Endpoint Control:** `GET /api/health`, `POST /api/generate`, and `POST /api/extend`.
* **Sidecar Telemetry:** GPU CUDA detection, VRAM allocation strategy (`enable_model_cpu_offload`), and model load state.
* **Controls:** Aspect ratios (`16:9`, `9:16`, `1:1`), Frame count slider (`16` to `121`), Guidance Scale (`1.0` to `15.0`).

### 3.3 Stock & Personal Media Providers
* **Free Stock:** Pexels, Pixabay, Coverr, Mixkit, NASA Public Domain.
* **Personal & Cloud Media:** Jellyfin Media Server, Plex Media Server, Google Veo / Omni Flash.

---

## 4. Architectural Requirements

* **Local-First & Privacy Preserving:** Operates fully local when configured with Ollama/LMStudio, Edge-TTS/CosyVoice, and LocalGen sidecar.
* **Modular Provider Registry:** Plugin architecture in `src/videogen_mcp/providers/` for LLM, Stock, and TTS layers.
* **Resilient Error Recovery:** Automatic fallbacks for Whisper alignment, cuBLAS CUDA missing libraries, and FFmpeg compose errors.

---

## 5. Success Metrics

* **Performance:** Local clip generation under 60s for 81-frame draft sequences on consumer GPUs (RTX 4090/3090).
* **Quality & Continuity:** Zero color drift across multi-clip extensions using LongCat-Video continuation logic.
* **Stability:** 100% test coverage pass rate on pytest backend suite and TypeScript `npx tsc --noEmit`.

---

*Maintained by: Antigravity AI Product Engineering · 2026*
