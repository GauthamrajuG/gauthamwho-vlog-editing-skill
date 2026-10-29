import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Ghost } from "./Ghost";
import { at, H, W } from "../airfryer/StyleFrame";
import track from "./track.json";

/**
 * The walk-in scare, one frame per frame of the shot (local frame 0 = v6 36.15 s).
 * Every pose comes from work/ghost-mg/motion.py (track.json): the position is
 * locked to his shoulder and head from the cut-out, with the spring rise, the
 * breathing, the anticipation and the curved swoop already solved there, plus
 * the hem's lag (drag) and the cloth ripple (phase). This file only draws it.
 */
type Pose = {
  x: number;
  y: number;
  s: number;
  rot: [number, number, number];
  eyes: number;
  drag: [number, number];
  phase: number;
  visible: boolean;
};

const TRACK = track as unknown as Pose[];
export const GHOST_FRAMES = TRACK.length;

export const GhostMotion: React.FC = () => {
  const p = TRACK[Math.min(useCurrentFrame(), TRACK.length - 1)];
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
        {p.visible ? (
          <group position={at(p.x, p.y)} rotation={p.rot} scale={p.s}>
            <Ghost eyes={p.eyes} drag={p.drag} phase={p.phase} />
          </group>
        ) : null}
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
