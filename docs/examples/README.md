# Example renders

Shipped samples produced by **ittybitty** (not placeholders).

| File | Description |
|------|-------------|
| *(coming soon)* `gsd-puppy-short.mp4` | Vertical short from home-library or Pexels B-roll |
| `cats-facts-short.mp4` | Legacy smoke-test sample (~23 s); may be removed from git to keep the repo lean |

Reproduce a test render:

```powershell
pip install -e .
# PEXELS_API_KEY + FFmpeg on PATH in .env
py scripts/smoke_render.py
```

The smoke script uses the same narration as the Generate page sample (`scripts/smoke_render.py`).
