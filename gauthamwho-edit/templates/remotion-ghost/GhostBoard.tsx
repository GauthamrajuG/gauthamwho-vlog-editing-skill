import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Ghost } from "./Ghost";
import { at, H, W } from "../airfryer/StyleFrame";

/**
 * Storyboard v3 poses, one per frame, rendered on transparency and composited
 * onto the real frames. Positions are screen pixels of the eye line; his LEFT
 * shoulder is the screen-right side (its top is at shoulder_y in
 * work/ghost-mg/board/geom.json).
 * drag = how far the hem trails behind the motion (local units), rot = [x, y, z].
 */
type Pose = {
  x: number;
  y: number;
  s: number;
  rot: [number, number, number];
  eyes: number;
  drag: [number, number];
  phase: number;
};

export const BOARD: Pose[] = [
  // 36.30 rising behind his left shoulder: only the hood top shows above it
  {
    x: 965,
    y: 1495,
    s: 0.95,
    rot: [0.05, -0.3, -0.04],
    eyes: 0,
    drag: [0.04, -0.25],
    phase: 0,
  },
  // 36.60 risen to his shoulder line, settling (the hem still catching up)
  {
    x: 950,
    y: 1366,
    s: 0.95,
    rot: [0.05, -0.35, 0.12],
    eyes: 0.25,
    drag: [-0.06, 0.12],
    phase: 1.2,
  },
  // 36.95 eyes ignite, leaning towards his neck
  {
    x: 938,
    y: 1372,
    s: 0.95,
    rot: [0.05, -0.4, 0.2],
    eyes: 1,
    drag: [0.05, 0.02],
    phase: 2.2,
  },
  // 37.30 anticipation: draws back and sinks a little before the swoop
  {
    x: 978,
    y: 1318,
    s: 0.95,
    rot: [0.05, -0.25, -0.08],
    eyes: 1.2,
    drag: [-0.08, 0.05],
    phase: 3.0,
  },
  // 37.55 swooping behind his neck to the other side, body trailing right
  {
    x: 360,
    y: 1360,
    s: 0.95,
    rot: [0.05, -0.1, 0.35],
    eyes: 1,
    drag: [0.95, -0.15],
    phase: 4.4,
  },
  // 37.75 rising out over his right shoulder (screen left), banking, hem streaming
  {
    x: 70,
    y: 1040,
    s: 0.95,
    rot: [0.05, 0.1, 0.55],
    eyes: 0.9,
    drag: [1.1, -0.65],
    phase: 5.6,
  },
];

export const GhostBoard: React.FC = () => {
  const p = BOARD[Math.min(useCurrentFrame(), BOARD.length - 1)];
  return (
    <AbsoluteFill>
      <ThreeCanvas
        width={W}
        height={H}
        camera={{ fov: 30, position: [0, 0, 10] }}
        gl={{ alpha: true, antialias: true }}
      >
        <ambientLight intensity={0.06} />
        <directionalLight
          position={[-1, 6, -1.5]}
          intensity={1.6}
          color="#e8e6f0"
        />
        <directionalLight
          position={[3, 1, -4]}
          intensity={0.35}
          color="#b9c4d6"
        />
        <directionalLight
          position={[-4, -1.5, 4]}
          intensity={0.75}
          color="#ffd9b0"
        />
        <group position={at(p.x, p.y)} rotation={p.rot} scale={p.s}>
          <Ghost eyes={p.eyes} drag={p.drag} phase={p.phase} />
        </group>
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
