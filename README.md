<p align="center"><img src="assets/banner.svg" alt="GauthamWho.edit: a Claude Code skill for clean vlog edits, original ideas and real-looking 3D in real footage" width="100%"></p>

# GauthamWho edit

A set of **Claude Code skills** that edit my own phone vlogs (Instagram **@GauthamWho**, Tamil
day-in-the-life reels shot on an iPhone) **exactly the way I like them**. They also come up
with ideas nobody else would think of, and put **real-looking 3D objects and characters** into
my real footage.

You drop a video in a folder, type one command, answer a few questions, and get back a
finished reel. Every rule in here came from me approving or rejecting real edits of Reel 29.

---

## The three commands

| Type in Claude Code | What it does | You get |
|---|---|---|
| `/gauthamwho-edit D:\Claude\Video\Reel 30` | **Clean edit.** Cuts the dead air while I talk, adds a few face punch-ins, and keeps my iPhone colour. | 2 video files: one to post (SDR) and one HDR |
| `/gauthamwho-ideas D:\Claude\Video\Reel 30` | **Ideas only.** Studies the clip and invents graphic moments. **Nothing is built.** | A list of opportunities, the top 3 ideas sketched on my real frames, and more ideas in one line each |
| `/gauthamwho-start D:\Claude\Video\Reel 30` | **Edit + ideas together**, in one message. | The edit questions and an idea menu. The edit gets built, then the ideas I pick get made |
| `/gauthamwho-edit D:\Claude\Video\Reel 30 at 0:36 a ghost rises behind my left shoulder…` | **My own graphic from my script.** | That graphic, step by step: beat sheet → storyboard → still → preview → full video |

> Slash commands can't contain spaces, so the names use dashes.
> When I say "left" or "right", I always mean **my own body's** left and right.

```mermaid
flowchart LR
  V(["My rough clip<br/>in a folder"]) --> Q{"Which command?"}
  Q -->|"/gauthamwho-edit"| E["Clean edit"]
  Q -->|"/gauthamwho-ideas"| I["Idea menu<br/>nothing built"]
  Q -->|"/gauthamwho-start"| B["Edit questions<br/>+ idea menu"]
  E --> F["Reel30_clean_SDR.mp4<br/>ready to post"]
  B --> F
  I --> P{"I pick ideas"}
  B --> P
  P --> G["Graphics, step by step<br/>with my OK each time"]
  G --> FV["Final video/<br/>GauthamWho_Reel30_Topic_v2_SDR.mp4"]
  F --> FV
```

---

## 1. `/gauthamwho-edit`: the clean edit

### What it does to the video

![Before and after: pauses removed, protected moments kept whole, a punch-in held to the next jump cut](assets/cut-timeline.svg)

- **My order stays exactly as I edited it.** Nothing is reordered, and there are no hooks.
- **Pauses longer than 0.25 s while I talk are cut**, and stammers and repeated takes are
  removed. It never cuts inside a word: it knows the time of every Tamil word.
- **My little sequences stay whole:** plug in → switch on; show the bag → drop it → black clip →
  walk in.
- **The opening plays uncut.**
- **One 130 % face punch-in per talking scene**, on its strongest line, with my eyes always on
  the same line.
- **No music, transitions, captions or effects.** I add captions myself later.

### The punch-in (the only effect)

<p align="center"><img src="assets/punch-in.jpg" alt="Left: normal framing. Right: the 130 percent punch-in, a hard cut with the eyes on the upper third line" width="480"></p>

*Left: normal framing. Right: a hard cut to 130 %, with my eyes on the upper-third line. It holds
until the next jump cut, so the cut back hides inside a cut that's already there.*

### What happens, step by step

```mermaid
sequenceDiagram
  autonumber
  participant Me
  participant Claude
  participant PC as My PC tools
  Me->>Claude: /gauthamwho-edit D:\...\Reel 30
  Claude->>PC: memory check, shots, Tamil words + English translation
  Claude->>Me: shot list, length, stammers, up to 4 questions
  Me->>Claude: answers
  Claude->>PC: cut plan (no word cut), eye points, build (~15 min)
  Claude->>PC: checks: 13 Instagram checks, Dolby Vision, 60 fps
  Claude->>Me: 2 files + every punch-in and cut listed
  Me->>Claude: "approved" or "change X"
```

**The 4 questions it asks** (each with my usual answer pre-selected):
1. Where does the uncut opening end?
2. Which moments must play completely uncut?
3. Which lines get a punch-in?
4. What to do with silent shots?

### Why the colour stays like my iPhone

```mermaid
flowchart LR
  O["iPhone clip<br/>Dolby Vision HDR"] --> H["HDR file<br/>Dolby Vision kept"]
  O --> S["SDR file<br/>made from the clip's own<br/>Dolby Vision mapping"]
  S --> IG(["Instagram:<br/>looks the same on every phone"])
  O -. "generic tools" .-> X(["flat, grey<br/>rejected"])
```

---

## 2. `/gauthamwho-ideas`: the creative engine

This is the part that thinks of moments **nobody else would**. The ghost was one of them: a
scare for people scrolling alone at midnight, unrelated to the script, and the kind of thing
they remember.

**How it thinks:**

```mermaid
mindmap
  root((My clip))
    Read the set
      dark corners, stairs, doors
      objects I touch
      my words and glances
      when people watch it
    10 lenses
      take my words literally
      hidden passenger
      the viewer's moment
      objects with a personality
      physics breaks
      second-watch easter egg
      running lore across reels
      the answered glance
      scale shift
      inversion
    Filter
      10-second test
      surprising but safe
      fits the real frame
      worth sending to a friend
      1 to 3 per reel
```

- **The 10-second test:** if three other creators would think of an idea within 10 seconds,
  it's thrown out.
- **Surprising but safe:** it breaks a rule but still feels fun. The science behind this is
  benign violation theory.
- **Worth sending:** Instagram's top signals are watch time, likes and **sends**. So ideas are
  built to make people send the reel: "did you see what's behind him at 0:36? 😱"

**How ideas are scored** (an illustration of the 1–5 scoring, not real data):

```mermaid
xychart-beta
  title "Example: scoring three ideas (1-5)"
  x-axis ["Surprise", "Sends", "Fits frame", "Easy to make", "On brand"]
  y-axis "score" 0 --> 5
  bar [5, 5, 4, 3, 5]
  line [3, 2, 5, 5, 4]
```

*Bars: a hidden-passenger scare. Line: a safer "object with a personality" gag. The top 3 by
total score are sketched for me.*

**What I get back:** the opportunity list with times, the top 3 ideas sketched on my real
frames, and 4–7 more ideas in one line each. Then I choose.

**Lore:** `D:\Claude\Video\lore.md` remembers recurring characters, like the wrist-hand, the
globe and the ghost. A later reel can bring one back half-hidden so fans start hunting for it,
and the same gag is never repeated the same way.

---

## 3. Story graphics: real-looking 3D in my real footage

### Example 1: "after I switch on the air fryer, the world gets slow" (Reel 29 v6)

<p align="center"><img src="assets/air-fryer.jpg" alt="A modelled air fryer with a hand clicking its button and a globe; the globe slows and glides behind his head" width="720"></p>

A 3D air fryer drops in, and a little wrist-hand clicks its button. A globe spinning left to
right slows to a crawl. On "slow" the fryer is thrown away and the globe glides **behind my
head**, then whips off with a stretch.

### Example 2: the midnight ghost (Reel 29 v7)

<p align="center"><img src="assets/ghost-final.jpg" alt="A dark hooded ghost with red eyes behind his left shoulder lighting him red, then swooping behind his neck and out" width="720"></p>

A dark hooded ghost rises behind my **left** shoulder, only to shoulder level. Its red eyes
**light up my hair, ear and the wall** like real light. Then it swoops **behind my neck** on a
curve and out over my right shoulder. I never react to it.

### Every graphic goes through these steps, with my yes at each one

```mermaid
flowchart LR
  A(["My idea<br/>or script"]) --> B["Beat sheet<br/>what happens, frame by frame"]
  B --> C{{"OK?"}} --> D["Storyboard<br/>real 3D on my real frames"]
  D --> E{{"OK?"}} --> F["One still<br/>full quality"]
  F --> G{{"OK?"}} --> H["Animation +<br/>4-5 s preview with sound"]
  H --> I{{"OK?"}} --> J["Swapped into the<br/>full video, next version"]
```

<p align="center"><img src="assets/ghost-storyboard.jpg" alt="Storyboard: six panels of the ghost rising, eyes igniting, drawing back, swooping behind and leaving" width="720"></p>

*The approved ghost storyboard. Blue dots show the parts hidden behind me or in the dark, and
the yellow line is its exit path.*

### The 12 realism rules (every object, every frame)

| # | Rule | What it means |
|---|---|---|
| 1 | **Whole object, always** | Full body, even the parts hidden behind me. Never cut off in a straight line or faded out "because it's not seen" |
| 2 | **Depth** | I'm cut out on every frame (with hair strands), so things can go behind me |
| 3 | **Locked to the scene** | It sticks to me or to the room. Tracking is used only if it's accurate |
| 4 | **Lit by the room** | The same light direction and colour as my real scene |
| 5 | **Matched to the footage** | Same blacks, warmth, softness, blur by distance, camera grain, motion blur |
| 6 | **Shadows** | A soft shadow on the nearest surface |
| 7 | **Its light lights the world** | Glowing eyes or screens really light my face and the walls |
| 8 | **Moves like it's alive** | Bounce, wind-up, curves, trailing cloth, breathing. No sticker slides |
| 9 | **My body's sides** | "Left shoulder" means my left (the right of the screen) |
| 10 | **Soft sound, only for the graphic** | No glitches, sparkles, buzzers or risers |
| 11 | **Checked twice** | Frame by frame, before I see anything |
| 12 | **60 fps, no AI video, no paid services** | Everything is made on my own PC |

---

## What it uses

```mermaid
flowchart TB
  subgraph EDIT["Clean edit"]
    FF["ffmpeg full build<br/>cuts, Dolby Vision, SDR"]
    PY["Python + faster-whisper<br/>Tamil word timings"]
    FS["ffmpeg-skill<br/>shots, checks"]
  end
  subgraph GFX["Story graphics"]
    SAM["SAM 2.1 on the GPU<br/>cuts me out of every frame"]
    RM["Remotion + three.js<br/>3D models and motion"]
    CP["Python compositing<br/>grade, light, depth, grain"]
  end
  subgraph BRAIN["Knowledge it reads at each stage"]
    K1["realism + motion blur:<br/>business-motion-film"]
    K2["camera + framing:<br/>directing-live-video, shot-recipes, shot-composition"]
    K3["physics:<br/>animation-principles, motion-doctrine"]
    K4["3D plumbing:<br/>13 threejs-* skills"]
    K5["compositing checklist:<br/>vendor/vfx-compositing"]
  end
```

The full map of which skill is read at which stage is `gauthamwho-edit/reference/skill-routing.md`.
It also lists the skills that are **never** used: anything with paid APIs or AI video.

---

## Install

1. Copy these three folders into your Claude Code skills folder
   (`C:\Users\<you>\.claude\skills\` on Windows, `~/.claude/skills/` on Mac/Linux):
   `gauthamwho-edit`, `gauthamwho-ideas`, `gauthamwho-start`.
   ```bash
   git clone https://github.com/GauthamrajuG/gauthamwho-vlog-editing-skill
   ```
2. For story graphics, also copy the 13 `skills/threejs-*` folders from
   [CloudAI-X/threejs-skills](https://github.com/CloudAI-X/threejs-skills) (MIT).
3. Restart Claude Code and type `/gauthamwho`. All three commands appear.

On the first run, Claude checks what's missing and **asks before installing anything**.

| Needed | For | About |
|---|---|---|
| Git, Python 3.10+, Node.js | running the skill | 500 MB |
| ffmpeg **full build** (gyan.dev) + a Vulkan GPU | cutting, Dolby Vision, the SDR file | 170 MB |
| ffmpeg-skill, faster-whisper, OpenCV 4 | analysis, Tamil words, eye grids | 600 MB |
| NVIDIA GPU (4 GB+), PyTorch CUDA, SAM 2.1 | cutting me out (graphics only) | 3.5 GB |
| Remotion + three.js | 3D graphics only | 500 MB |

Built and tested on Windows 11, 7.5 GB RAM, GTX 1650. If a build crashes with "out of memory",
end the leaking Windows service **AppXSvc** in Task Manager (Details → the `svchost.exe` using
several GB → End task).

---

## What's inside, and do I ever touch it?

**Short answer: no. You never open, call or link these files.** You only type one of the three
commands. Claude then opens the right files **by itself**, in the right order, like a crew
member reaching for the right tool. The files are the skill's **memory and toolbox**.

```mermaid
flowchart LR
  ME(["You type<br/>/gauthamwho-start Reel 30"]) --> C["Claude"]
  C -->|"reads first"| S["SKILL.md<br/>the rulebook"]
  S -->|"when it needs ideas"| CE["creative-engine.md<br/>the idea method"]
  S -->|"when it builds a graphic"| SG["story-graphics.md<br/>the graphics recipe"]
  SG -->|"for camera, light, motion..."| SR["skill-routing.md<br/>which expert to ask"]
  SR --> V["vendor/ + other skills<br/>the experts' notes"]
  S -->|"for exact commands"| PL["pipeline.md<br/>the technical manual"]
  S -->|"to do the work"| SC["scripts/<br/>the tools"]
  SG -->|"to start a 3D model"| T["templates/<br/>3D models to reuse"]
```

Think of it like a film crew. `SKILL.md` is the **director's rulebook**, the reference files are
the **department handbooks**, `scripts/` are the **machines**, and `templates/` is the **props
store**.

### Each part, with an example of when it's used

#### 📕 `gauthamwho-edit/SKILL.md`: the rulebook
- **What:** everything about your style: "cut pauses over 0.25 s", "one 130 % punch-in per
  scene", "never music", "left means your left", the 12 realism rules, the red flags.
- **When it's used:** on **every** command, first.
- **Example:** you say "make it high retention". The rulebook makes Claude cut pauses and add
  punch-ins, **not** add music and transitions like other editors would.

#### 💡 `gauthamwho-edit/reference/creative-engine.md`: the idea method
- **What:** how to find ideas nobody else has. Read the set, use 10 lenses, throw out
  anything generic, score the rest, sketch the top 3.
- **When it's used:** `/gauthamwho-ideas`, `/gauthamwho-start`, or whenever you say "give me ideas".
- **Example:** it notices a dark staircase at 0:36 and that the reel goes out at night. The
  "hidden passenger" lens plus the "viewer's moment" lens give the ghost idea.

#### 🎬 `gauthamwho-edit/reference/story-graphics.md`: the graphics recipe
- **What:** the full step-by-step way to put 3D into your footage, with the air fryer and the
  ghost written up as worked examples, including what you corrected along the way.
- **When it's used:** when a graphic is being made.
- **Example:** before making a new creature, Claude reads how the ghost was done. It learns
  "full body, never a straight cut", "rise only to shoulder level", "anchor to the shoulder",
  and does it right the first time.

#### 🧭 `gauthamwho-edit/reference/skill-routing.md`: which expert to ask
- **What:** a map of the other skills on your PC. For each stage (camera, lighting, motion,
  framing, review…) it names the best skill to read. It also lists the **banned** skills that
  use paid APIs or AI video.
- **When it's used:** during graphics work, stage by stage.
- **Example:** planning a camera move, Claude reads *directing-live-video*'s camera notes. For
  motion blur it reads *business-motion-film*. It never touches *kvk-make-a-video*, which uses
  paid AI video.

#### 🔧 `gauthamwho-edit/reference/pipeline.md`: the technical manual
- **What:** exact commands, which tools are installed where, and fixes for your PC (like the
  AppXSvc memory leak).
- **When it's used:** whenever Claude runs ffmpeg, the transcriber or a build.
- **Example:** a build crashes with "out of memory". The manual tells Claude it's AppXSvc, so it
  asks **you** to end it in Task Manager instead of guessing.

#### ⚙️ `gauthamwho-edit/scripts/`: the machines
Small programs Claude runs for you. You never run them yourself.

| Script | What it does | Example |
|---|---|---|
| `transcribe.py` | writes down your Tamil speech with the time of every word, plus English | knows exactly when each word of "who'll put petrol?" is said, so a cut never lands inside a word |
| `plan_cuts.py` | turns your answers + the words into the list of cuts | removes a 1.1 s pause, keeps your "plug → switch on" whole |
| `eye_grid.py` | puts a grid on a frame so your eye position can be measured | places the punch-in so your eyes sit on the upper third |
| `build_reel.py` | builds the two final videos from the original clip | makes `Reel30_clean_SDR.mp4` and `Reel30_clean_HDR.mp4` |
| `graphics/cutout_all.py` | cuts you out of every frame (AI on your graphics card) | lets the globe go **behind** your head |
| `graphics/compose_*.py` | blends the 3D into your footage: colour, grain, shadow, light | makes the air fryer look like it's in your room |
| `graphics/sfx.py` | makes the little sound effects from scratch (nothing downloaded) | the click of the air fryer button |
| `graphics/ghost/…` | the ghost's tools: motion, red light, preview | makes the ghost's red eyes light your hair |

#### 🧸 `gauthamwho-edit/templates/`: the props store
- **What:** the 3D models already built: the air fryer, the wrist-hand, the globe, the ghost.
- **When it's used:** when a new graphic needs something similar.
- **Example:** a new reel needs a toaster. Claude starts from the air fryer's body, buttons and
  materials instead of from zero, so it's faster and keeps the same quality.

#### 📚 `gauthamwho-edit/vendor/`: notes from outside experts
- **What:** three free (MIT) professional guides: VFX compositing, camera/shot direction, and
  short-video production.
- **When it's used:** only when our skill calls them. They can **never** take over your edit on
  their own, for example by adding captions or music.
- **Example:** before the final check, Claude runs the compositing guide's 7-step check,
  including viewing it at phone size.

#### ⌨️ `gauthamwho-ideas/` and `gauthamwho-start/`: the extra commands
- **What:** tiny files that create the `/gauthamwho-ideas` and `/gauthamwho-start` commands.
  Each one says "run this part of gauthamwho-edit".
- **When it's used:** only when **you** type that command. Claude never starts them by itself.

#### 🖼️ `assets/`: pictures for this page
Only used by this README. The skill doesn't need them.

### Does anything run automatically?

| | Runs by itself? | How it starts |
|---|---|---|
| `/gauthamwho-edit` | **Yes**, if you say things like "edit this reel" or "add a ghost at 0:36" | or type `/gauthamwho-edit` |
| `/gauthamwho-ideas` | No | you type `/gauthamwho-ideas` |
| `/gauthamwho-start` | No | you type `/gauthamwho-start` |
| everything in the table above | Yes, **Claude opens them for you** | never by you |

### Want to change a rule?

Don't edit the files by hand. Just tell Claude in plain words, for example:

> "Update my gauthamwho skill: punch-ins should be 120 %, not 130 %."

> "Add to my skill: never put graphics on food shots."

Claude changes the right file. Ask it to push to GitHub and every computer gets the new rule.

Credits: vendored guides from [calesthio/generative-media-skills](https://github.com/calesthio/generative-media-skills) (MIT).
The idea methods draw on Oblique Strategies, SCAMPER, benign violation theory (McGraw & Warren 2010),
jump-scare craft write-ups, and Instagram's published ranking signals.
