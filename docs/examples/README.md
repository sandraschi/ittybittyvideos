# Example renders

Shipped samples produced by roughcutvideos on this repo (not stock placeholders).

| File | Description |
|------|-------------|
| [cats-facts-short.mp4](./cats-facts-short.mp4) | ~23 s vertical short; custom script, Pexels B-roll, Edge TTS |
| [cats-facts-short-poster.jpg](./cats-facts-short-poster.jpg) | Poster frame for README / docs |

Reproduce the cats demo:

```powershell
pip install -e .
# PEXELS_API_KEY + FFmpeg on PATH in .env
py scripts/smoke_render.py
```

The smoke script uses the same narration as the Generate page sample script (`scripts/smoke_render.py`).
