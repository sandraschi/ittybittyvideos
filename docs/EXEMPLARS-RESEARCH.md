# Viral exemplar library — research & expansion playbook

Research for **R10 prompt director**, **GSD demo**, and mid-length **videographer** chapters.  
We emulate **structure**, not proprietary footage — use **Jellyfin/home clips** or licensed stock.

**Trope files:** [`templates/tropes/`](../templates/tropes/) · **Prompt library:** webapp `/prompts`

---

## How to use this doc

| Layer | Short (30–45s) | Mid-length (3–7 min) |
|-------|----------------|----------------------|
| **Hook** | 0–3s pattern interrupt | Cold open = best Short beat blown up cinematic |
| **Body** | 1–2s cuts, text overlays | Chapters = one beat per scene + B-roll inserts |
| **Payoff** | Loop to frame 1 | Act III reveal + recap chapter |
| **Audio** | Optional VO or ASMR | Full narration + R1 karaoke subs |

**Retention targets (Shorts):** >70% completion, visual change every **1.5–2s**, seamless **loop** where possible ([retention playbook](https://aibrify.com/blog/youtube-shorts-retention-curve-playbook)).

---

## Catalog — multimillion-view formats to emulate

| Trope ID | Exemplar / genre | ~Views | Core hook | Expand to mid? |
|----------|------------------|--------|-----------|----------------|
| [`pet-food-duo-review`](../templates/tropes/pet-food-duo-review.yaml) | **Jade The Sable GSD** — picky vs eater, Yummy/Whazzat labels | **15M+** ([3 GSDs Review Foods](https://www.youtube.com/watch?v=sozQOCq5J7g)) | Two dogs, same morsel, opposite reactions | ★★★ Personality documentary |
| [`duo-unfair-portion`](../templates/tropes/duo-unfair-portion.yaml) | **Shiba Diva** — unfair sausage sizes | **61M+** ([video](https://www.youtube.com/watch?v=mlQvkFVGEJY)) | Jealousy / fairness arc | ★★★ Social experiment narrative |
| [`dog-tease-fridge`](../templates/tropes/dog-tease-fridge.yaml) | **Ultimate Dog Tease** (Clark) | **212M+** ([classic](https://www.youtube.com/watch?v=nGeKSiCQkPw)) | List foods → fake-out → tiny reward | ★★ Clip montage + VO list |
| [`before-after-reveal`](../templates/tropes/before-after-reveal.yaml) | Transformation / satisfying Shorts class | Format-wide | **Result first**, then how | ★★★ Tutorial / makeover |
| [`satisfying-process-loop`](../templates/tropes/satisfying-process-loop.yaml) | Clean-with-me / build timelapse | Format-wide | Process ASMR + loop | ★★★ 3-act process doc |
| [`countdown-three-things`](../templates/tropes/countdown-three-things.yaml) | "3 things" / listicle Shorts | Format-wide | Open loop #3→#1 | ★★★ Explainer chapters |
| [`myth-vs-truth`](../templates/tropes/myth-vs-truth.yaml) | Myth bust / contrarian take | Format-wide | MYTH text → TRUTH reveal | ★★★ Evidence + citations (R4) |
| [`story-hook-reveal`](../templates/tropes/story-hook-reveal.yaml) | Interruption / twist (proposal dog genre) | **47s → 200M+** case studies | Start mid-crisis, reveal late | ★★★ Full story arc |

### Adjacent pet memes (template energy, different beat)

| Meme | Scale | ittybitty use |
|------|-------|----------------|
| [Whining Dog / Hm hm hm](https://trending.knowyourmeme.com/editorials/guides/what-is-the-whining-dog-meme-the-german-shepherd-whining-in-many-tiktok-brainrot-memes-explained) | TikTok brainrot | Single-shot reaction + text graph overlay |
| [Dog With Apple (Hailuo AI)](https://knowyourmeme.com/memes/dog-with-apple-minimax-hailuo-ai-videos) | 2.8M+ per iteration | AI clip chain — **LocalGen** + absurd escalation |
| [Dancing AI Golden Retriever](https://knowyourmeme.com/memes/dancing-ai-golden-retriever-dog) | 1.2M–5M+ | Greenscreen template — not our core, but shows **sound + loop** power |
| **Strider GSD** taste tests | Multi-M per clip | Solo ASMR reject — pair with duo contrast |

---

## Deep dive: GSD food duo (your exemplar)

### Channel: **Jade The Sable GSD**

- YouTube: [@JadeTheSableGSD](https://www.youtube.com/@JadeTheSableGSD)
- TikTok: `@jadethesablegsd` — **“Picky Doggo vs Doggo Dumpster”** (parts @ 1.9M+)
- Dogs: Jade, **Jasper** (picky), Jet, Onyx

**Short beat sheet**

1. Tray of treats — split screen or sequential  
2. Hand offers morsel → **Dog A** munch → floating **“Yummy”**  
3. Same morsel → **Dog B** head tilt → **“Whazzat?”**  
4. Repeat 3–5× — escalate weird food  
5. Punchline: picky dog loves last item OR sibling swap  

**Mid-length expansion (5 chapters, ~4 min)**

| Ch | Scene types | Cinematography |
|----|-------------|----------------|
| 1 Hook | hook + intro | Handheld close on eyes; split diptych |
| 2 Meet the cast | intro + broll | Wide kitchen; name cards; personality VO |
| 3 Round 1–3 | demo ×3 | Macro crunch; alternating eyelines |
| 4 The twist food | demo + explainer | Slow-mo accept; skeptical → joy |
| 5 Recap | recap + outro | Side-by-side matrix; “who’s picky?” CTA |

**Footage:** `%JELLYFIN%` GSD clips — search tags `dog`, `gsd`, `kitchen`.

---

## Deep dive: Shiba Diva unfair portion (61M)

**Why it works:** injustice trigger → comment bait → fairness resolution.

**Short:** 36s, narration optional, music bed.

**Mid expansion:** frame as **experiment** — hypothesis, trials, data table overlay, “scientific” VO parody, then heartwarming fix.

---

## Deep dive: Ultimate Dog Tease (212M)

**Clark** the Dutch Shepherd — owner lists bacon, chicken, etc., dog hears every word, gets nothing (then tiny payoff).

**Short:** pure VO list + reaction cuts.

**Mid:** “Greatest teases compilation” + chapter per food + ethics disclaimer humor + training tip B-roll (fake).

---

## Generic viral Short anatomy (all tropes)

```mermaid
flowchart LR
  H[0-3s Hook] --> O[Open loop]
  O --> S[8-25s Stack micro-payoffs]
  S --> P[Payoff]
  P --> L[Loop to H]
```

| Second | Job |
|--------|-----|
| 0–1 | Pattern interrupt — motion or bold text |
| 1–3 | Open loop — unanswered question |
| 3–25 | Dopamine every 1.5–2s — cut, zoom, new text |
| 25–30 | Payoff + **no** “subscribe” hard stop |
| 30+ | Seamless loop → rewatch >100% |

---

## Short → mid-length expansion rules (ittybitty)

When `videogen_plan` with a trope id:

1. **Each Short beat → one chapter** (planner already outputs chapters).  
2. **Insert B-roll** every 3 A-roll scenes (videographer rule — already shipped).  
3. **Widen shots** on chapter open (wide/aerial); **close** on emotional beat.  
4. **R2 beat snap** on montage chapters; duck VO under BGM on recap.  
5. **R3 screening** flags mismatched stock vs narration on longform.  
6. **Duration rebalancing** — target 4–6 min unless user asks 15 min documentary.

**Example mapping** (`pet-food-duo-review`):

```
Short loop (45s)          →  Mid (300s)
─────────────────────────────────────────
hook (3s)                 →  Ch1 hook + cast intro (45s)
demo loop ×3 (24s)        →  Ch2–4 one food each (60s ea)
punchline (8s)            →  Ch5 twist + outro (45s)
```

---

## Absurd credits + post-credits (`trope:absurd-credits-roll`)

Pixar’s **~2,000-name scroll** is the joke — baby names, fake departments, historical cameos. We emulate structure, not their footage.

**Credits pack:** `templates/credits/absurd-pixar.yaml`

| Featured | Role |
|----------|------|
| Albert Einstein | Relativity Advisor |
| Attila the Hun | Strategy Consultant |
| Cleopatra | Treat Allocation Pharaoh |
| Socrates | Chief "Whazzat?" Philosophical Review |

Also: departments (*Canine Morale*, *Bork Foley*), joke pool (*Three Raccoons in a Trenchcoat*), numbered filler (*Treat Wrangler #47*), and **post-credits stingers**.

**Short:** main bit → tease credits → scroll segment → stinger after “THE END”.  
**Mid:** fake ending → credits I (featured) → credits II (filler army) → post-credits scene.

**API:** `GET /api/v1/credits/sample?pack=absurd-pixar` · MCP `videogen_credits_sample`.  
**Future:** FFmpeg scroll card (R7 visual template) — today = LLM narration + scene notes.

---

## Legal & ethics

- Do **not** re-upload Jade, Shiba Diva, or Clark source videos.  
- **Structure + original footage** only.  
- AI-generated dog clips: disclose if publishing; avoid impersonating real creator pets.  
- “Yummy / Whazzat” = generic meme captions, not brand assets.

---

## ittybitty checklist

- [x] Trope YAML seeds in `templates/tropes/`  
- [x] Prompt library structure presets (`trope:*`)  
- [x] Wire `structure` → `prompt_director.py` (R10 backend)  
- [ ] GSD demo render from Jellyfin + `pet-food-duo-review`  
- [ ] Mid-length test: same trope at 300s with chapter previews  

---

## References

- [Jade — 3 German Shepherds Review Foods](https://www.youtube.com/watch?v=sozQOCq5J7g)  
- [Shiba Diva — two dogs snacks](https://www.youtube.com/watch?v=mlQvkFVGEJY)  
- [Ultimate Dog Tease](https://www.youtube.com/watch?v=nGeKSiCQkPw)  
- [Laughing Squid — Jade coverage](https://laughingsquid.com/three-german-shepherds-review-foods/)  
- [Viral Shorts dataset patterns](https://theviralsauce.com/playbooks/viral-youtube-shorts-dataset-analysis)  
- [Retention curve playbook](https://aibrify.com/blog/youtube-shorts-retention-curve-playbook)  
- [PROMPT-DIRECTOR.md](./PROMPT-DIRECTOR.md) · [SPEC.md § R10](../SPEC.md)
