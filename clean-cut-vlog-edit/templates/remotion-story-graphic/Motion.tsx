import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { AirFryer, BUTTON } from "./AirFryer";
import { Hand } from "./Hand";
import { Globe } from "./Globe";
import { Studio } from "./Studio";
import { H, W } from "./StyleFrame";

/**
 * The "world slows down" beat, Reel 29 v5 frames 3450-3822 (57.500-63.717 s),
 * 373 frames at 60 fps. 3D objects only, on transparency, in the coordinates of
 * the plate's reference frame 66 (58.6 s, the approved style frame). The
 * compositor tracks this layer to the camera, grades it, puts him on top and
 * applies the punch-in crop from frame 130.
 */
export const MG_FRAMES = 373;
const PUNCH = 130;

const K = (2 * 10 * Math.tan((15 * Math.PI) / 180)) / H;
const px = (x: number, y: number): [number, number, number] => [
  (x - W / 2) * K,
  (H / 2 - y) * K,
  0,
];
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** Globe spin: fast until the press, eased down to a slow turn, then constant. */
const W_FAST = 0.28;
const W_SLOW = 0.008;
const speedAt = (f: number) => {
  if (f < 72) return W_FAST;
  if (f < 116)
    return lerp(W_FAST, W_SLOW, Easing.out(Easing.cubic)((f - 72) / 44));
  return W_SLOW;
};
const SPIN_AT: number[] = (() => {
  const s = [0];
  for (let f = 1; f < MG_FRAMES; f++) s.push(s[f - 1] + speedAt(f));
  return s;
})();
// India faces the viewer when the globe settles behind him (frame 176).
const SPIN_OFFSET = 2.93 - SPIN_AT[176];

export const AirFryerMotion: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ---- air fryer -----------------------------------------------------------
  const drop = spring({
    frame: f - 6,
    fps,
    config: { damping: 13, stiffness: 140, mass: 0.9 },
  });
  const tray = spring({
    frame: f - 18,
    fps,
    config: { damping: 16, stiffness: 120 },
  });
  const throwT = interpolate(f, [PUNCH + 1, PUNCH + 28], [0, 1], {
    ...clamp,
    easing: Easing.in(Easing.quad),
  });
  const fryerPos = px(
    lerp(250, -520, throwT),
    lerp(430 - (1 - drop) * 520, 230, throwT),
  );
  const fryerRot: [number, number, number] = [
    0.2 + throwT * 0.8,
    -0.36 - throwT * 1.6,
    (1 - drop) * -0.25 + throwT * 2.2,
  ];
  const fryerScale = 0.78 * interpolate(drop, [0, 1], [0.88, 1]);

  // ---- hand: pops up, taps, pops out ----------------------------------------
  const handIn = spring({
    frame: f - 58,
    fps,
    config: { damping: 15, stiffness: 220 },
  });
  const handOut = interpolate(f, [84, 98], [0, 1], {
    ...clamp,
    easing: Easing.in(Easing.cubic),
  });
  const tap = interpolate(f, [66, 72, 78, 84], [0, 1, 1, 0], clamp);
  const handVisible = f >= 58 && f < 98;
  const handOffset: [number, number, number] = [
    BUTTON[0],
    BUTTON[1] - (1 - handIn) * 0.75 - handOut * 0.75,
    BUTTON[2] + 0.06 + (1 - handIn) * 0.35 + handOut * 0.35 - tap * 0.055,
  ];
  const handScale = Math.max(0.001, handIn * (1 - handOut));
  const press = interpolate(f, [68, 72, 80, 86], [0, 1, 1, 0], clamp);
  const flash = interpolate(f, [72, 84], [1.6, 1], clamp);
  const on = f < 72 ? 0 : flash;

  // ---- globe ---------------------------------------------------------------
  const pop = spring({
    frame: f - 8,
    fps,
    config: { damping: 11, stiffness: 160 },
  });
  const glide = interpolate(f, [PUNCH + 2, 176], [0, 1], {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
  const squash = interpolate(f, [345, 352], [0, 1], {
    ...clamp,
    easing: Easing.out(Easing.quad),
  });
  const whip = interpolate(f, [352, 370], [0, 1], {
    ...clamp,
    easing: Easing.in(Easing.cubic),
  });
  const gx = lerp(lerp(860, 530, glide), 1500, whip);
  const gy = lerp(lerp(400, 700, glide), -520, whip);
  const gScale = Math.max(0.001, pop * lerp(1, 1.6, glide));
  // squash before the whip, then stretch along the direction of travel
  const along = whip > 0 ? 1 + whip * 0.9 : 1 - squash * 0.06;
  const across = whip > 0 ? 1 - whip * 0.35 : 1 + squash * 0.06;
  const dirAngle = Math.atan2(-(-520 - 700), 1500 - 530); // screen y is down, world y is up
  const spin = SPIN_AT[Math.min(f, MG_FRAMES - 1)] + SPIN_OFFSET;

  return (
    <AbsoluteFill>
      <ThreeCanvas
        width={W}
        height={H}
        camera={{ fov: 30, position: [0, 0, 10] }}
        gl={{ alpha: true, antialias: true }}
      >
        <Studio />
        {f >= 6 && throwT < 1 ? (
          <group position={fryerPos} rotation={fryerRot} scale={fryerScale}>
            <AirFryer trayIn={Math.min(1, tray)} on={on} press={press} />
            {handVisible ? (
              <group
                position={handOffset}
                rotation={[-0.62, 0.1, 0.12]}
                scale={handScale}
              >
                <Hand />
              </group>
            ) : null}
          </group>
        ) : null}
        {f >= 8 && whip < 1 ? (
          <group position={px(gx, gy)} scale={gScale}>
            <group rotation={[0, 0, dirAngle]}>
              <group scale={[along, across, 1]}>
                <group rotation={[0, 0, -dirAngle]}>
                  <Globe spin={spin} radius={0.42} />
                </group>
              </group>
            </group>
          </group>
        ) : null}
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
