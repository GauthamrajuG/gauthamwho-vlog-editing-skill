import React from "react";
import { AbsoluteFill } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { AirFryer, BUTTON } from "./AirFryer";
import { Hand } from "./Hand";
import { Globe } from "./Globe";
import { Studio } from "./Studio";
import { at, H, W } from "./StyleFrame";

/**
 * The 3D objects alone, on transparency — the layer that gets graded to the
 * footage, tracked to the camera and put behind him in the compositor.
 * The room's light is slightly warm and comes from the front-left, so the key
 * light is warmed to match.
 */
export const AirFryerCgLayer: React.FC = () => (
  <AbsoluteFill>
    <ThreeCanvas
      width={W}
      height={H}
      camera={{ fov: 30, position: [0, 0, 10] }}
      gl={{ alpha: true, antialias: true }}
    >
      <Studio />
      <group position={at(250, 430)} rotation={[0.2, -0.36, 0]} scale={0.78}>
        <AirFryer trayIn={1} on={1} press={0.6} />
        <group
          position={[BUTTON[0], BUTTON[1], BUTTON[2] + 0.005]}
          rotation={[-0.62, 0.1, 0.12]}
        >
          <Hand />
        </group>
      </group>
      <group position={at(860, 400)}>
        <Globe spin={2.2} radius={0.42} />
      </group>
    </ThreeCanvas>
  </AbsoluteFill>
);
