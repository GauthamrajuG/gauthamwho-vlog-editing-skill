---
name: gauthamwho-start
description: GauthamWho clean edit plus the creative engine in one go. One message with the clean-edit questions and a creative menu of the top 3 graphic ideas, then the clean edit is built and only the chosen ideas go through the graphics steps. Typed by the creator as /gauthamwho-start <folder or clip>.
disable-model-invocation: true
argument-hint: <folder or clip path>
---

# GauthamWho start: edit + ideas

Run the `gauthamwho-edit` skill's **Job A (clean edit)** and its **creative engine** together
on: $ARGUMENTS

1. Read `~/.claude/skills/gauthamwho-edit/SKILL.md` in full, then
   `reference/creative-engine.md`, `reference/skill-routing.md` and `D:/Claude/Video/lore.md`.
2. Machine check and analyse once (Job A steps 1–2). The same analysis feeds both jobs.
3. Send **one message** containing:
   - the Job A intake: the shot list, the defaults, the real estimated length, the stammers to
     remove, and its questions (at most 4, as in SKILL.md);
   - a **creative menu**: the opportunity inventory in 5–8 lines, the top 3 graphic ideas
     sketched on the real frames (one sheet), and the others in one line each;
   - a final question asking which ideas they want: none, any of them, or a mix.
   Use AskUserQuestion with at most 4 questions in total. If Job A needs all 4, ask about the
   ideas in the message text instead.
4. Build the clean edit as usual (Job A steps 4–8). The chosen ideas then go through the Job B
   approval ladder on the approved edit: beat sheet → storyboard with the real 3D → still →
   preview with sound → full video as the next version, with a yes at every step.
