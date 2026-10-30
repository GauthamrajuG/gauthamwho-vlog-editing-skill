import React from "react";
import { AbsoluteFill } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { Ghost } from "./Ghost";
import { at, H, W } from "../airfryer/StyleFrame";

/**
 * Style frame for the walk-in scare: the figure alone on transparency, posed
 * as storyboard panel 4 (v6 37.30 s, "leans in"). The compositor grades it to
 * the plate, adds the eye bloom and smoke, relights him and the walls with the
 * eyes' red light, and lays his cut-out back on top.
 * The stairwell's only light is the lamp above, so the figure gets a dim cool
 * top light and almost nothing else: it should read as a shape cut out of the dark.
 */
export const GhostStill: React.FC = () => (
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
      {/* the street light that lights the stairs comes from low front-left */}
      <directionalLight
        position={[-4, -1.5, 4]}
        intensity={0.75}
        color="#ffd9b0"
      />
      <group
        position={at(872, 856)}
        rotation={[0.05, -0.32, 0.24]}
        scale={1.15}
      >
        <Ghost eyes={1} />
      </group>
    </ThreeCanvas>
  </AbsoluteFill>
);
