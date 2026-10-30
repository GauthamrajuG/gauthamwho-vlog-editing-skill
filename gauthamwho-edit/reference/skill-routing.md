# Job B skill routing: which skill to read at which stage

The creator's own rules (SKILL.md, story-graphics.md, creative-engine.md) override everything
below. Read only the named parts; ignore anything in them about music, captions, hooks,
re-cutting, transitions, flashes or harsh SFX unless the creator asked. Audited 2026-10-30.

Paths: user skills are in `~/.claude/skills/<name>`; the Remotion set is in
`D:/Claude/Video/.agents/skills/remotion-best-practices/`; `vendor/` is inside this skill.

| Stage | Read | What to take from it |
|---|---|---|
| **Ideas** | `reference/creative-engine.md` (ours) first; then motion-art-direction (one wow moment, restraint pass); short-form-edit `references/curiosity-and-entertainment.md` (expectation → development → payoff, draft 3 alternatives); directing-live-video `references/direction.md` §1 (tension curve 1–5 per beat) | the idea list and its scoring |
| **Beat sheet / storyboard** | directing-live-video `references/storyboard.md` + `direction.md`; motion-doctrine (causal chain click → squash → release → flight → impact → recoil; 0.3–0.75 s of stillness before the climax) | beats with frame numbers, the hold before the reveal |
| **Modelling / look** | business-motion-film `references/three-js-patterns.md`, `product-hero-realism.md`; threejs-materials, threejs-geometry, threejs-textures (color spaces); remotion-best-practices `remotion-markup/3d.md` | PBR materials, correct color space, no faceted silhouettes |
| **Lighting / compositing / grade** | `vendor/vfx-compositing/GUIDE.md` (2D/2.5D/3D choice, tracking checks, grain, sharpness, motion blur, contact shadows, QA); threejs-lighting (environment light, shadows, physical units); business-motion-film `product-hero-realism.md` §3–4; color-motion `references/color-management.md`; remotion-markup `color-correction.md`; remotion-render `transparent-videos.md` (alpha renders) | the realism checklist items 4–7 |
| **Motion / physics** | animation-principles (+ `references/twelve-principles.md`: anticipation 60–120 ms, follow-through, arcs, 1/3 rule); shot-recipes `lib/helpers` (dampedSettle, lagged, velocityAt, seeded handheld); puppet-characters / directing-live-video `engine/face.ts` timings (blinks every 2.5–5 s, breath with a 4-frame head lag, the eyes lead) for creatures | springs, lag, breathing |
| **Camera** | directing-live-video `references/camera.md` (spring presets: heavy ζ 1.0, steadicam 0.79, whip 0.69, snap 0.56; handheld amplitude by mood); shot-recipes camera cards (tension moves, crash zoom, depth-layer moves, speed-ramp-freeze); `vendor/cinematic-shot-direction/GUIDE.md` (dolly vs zoom parallax, height/angle, screen direction) | only moves that mean something |
| **Framing / focus** | shot-composition (9:16 safe areas: top ~12 %, bottom ~18–20 %, sides 6 %; one focal point on a thirds point; parallax 0.2 / 0.6 / 1.2×; depth blur + desaturation) | where the eye lands |
| **Frame rate / motion blur** | business-motion-film `product-hero-realism.md` §3 (sub-frame accumulation, shutter 180° rising to ~300° on fast moves, ramped over 6 frames); remotion-markup `motion-blur.md` | blur that matches the phone |
| **Transitions** (only if asked) | shot-recipes `transition/transition-hidden-cut.md`; directing-live-video `direction.md` §3 | hidden cuts only |
| **Sound** | directing-live-video `references/sound.md` (soft SFX, spacing) | never music |
| **Retention / pacing** | `vendor/social-short-production/GUIDE.md` (retention-curve shapes, mute-viewing pass); kvk-ai-editor-style timing only (a graphic lands 0.1–0.3 s after its key word; one overlay at a time) | when the graphic interrupts speech |
| **Review** | directing-live-video `references/review.md` (stills every 0.5 s, freezedetect, loudness); video-talkcraft `references/review-protocol.md` (a fresh reviewer subagent, P0/P1/P2 defects); business-motion-film `gauntlet.md` + `critic-prompts.md` (a fresh critic plots speed per frame, hunts single black frames) | the self-check, item 11 |

## Remotion caveats when reading three.js material

- Drive every animation from `useCurrentFrame()`. Never use R3F `useFrame`, `THREE.Clock` or
  an animation loop: renders are frame-by-frame and these flicker or freeze.
  (threejs-animation and threejs-react-three-fiber describe real-time loops: translate them.)
- `ThreeCanvas` needs explicit `width`/`height`; a `Sequence` inside it needs `layout="none"`.
- Render CG on transparency (`--image-format=png --sequence`, files are zero-padded
  `element-000.png`) and composite in Python, where the plate, matte and light are.

## Never use for this creator

kvk-3d-assets, kvk-make-a-video (paid Kie.ai, mandatory AI images/video, an API key inside
the scripts), ecc:fal-ai-media, ecc:video-editing (ElevenLabs/fal.ai), ecc:videodb (cloud),
generate-image (paid OpenRouter), the paid/AI-video routes of media-use, business-motion-film
step 4 (AI stills/video), video-talkcraft's Fish Audio TTS. Also skip the ecc
motion-foundations / motion-patterns / motion-advanced / motion-ui set (real-time UI motion,
it flickers in frame renders) and retention-editing / short-form-edit as processes (music,
captions, hooks).

## Gaps (not covered by any skill yet; candidates to build)

- A 3D camera solve for handheld iPhone shots (COLMAP / solvePnP / the phone's gyro data) into
  a `ThreeCanvas` camera with the right FOV, lens distortion and rolling shutter.
- A scene depth map (e.g. Depth Anything) so doors and furniture, not only the person, can
  hide a graphic.
- Reading the iPhone's shutter speed from metadata to set the CG motion blur exactly.
Each of these needs a large download: ask the creator first.
