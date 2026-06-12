# Trope templates (R10 — planned)

Curated narrative structure presets for the prompt director. One YAML file per trope.

**Not wired yet.** See [docs/PROMPT-DIRECTOR.md](../../docs/PROMPT-DIRECTOR.md) and [SPEC.md § R10](../../SPEC.md).

Example schema (draft):

```yaml
id: tutorial
label: Step-by-step tutorial
video_types: [tutorial, demo]
beats:
  - scene_type: hook
    narration_goal: State the problem in one punchy sentence
    duration_hint: 4
  - scene_type: explainer
    narration_goal: What the viewer will learn
  - scene_type: demo
    narration_goal: Step 1 with on-screen action
example_hook: "Your sourdough keeps failing at the fold — here's the fix."
```

Ship targets: `tutorial`, `documentary`, `listicle`, `hype-short`, `explainer-problem-solution`, `recap-montage`.
