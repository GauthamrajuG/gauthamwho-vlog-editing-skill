import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { AirFryer, BUTTON } from "./AirFryer";
import { Hand } from "./Hand";
import { Globe } from "./Globe";
import { Studio } from "./Studio";

export const W = 1080;
export const H = 1920;

/**
 * Camera: fov 30 at z = 10, so the z = 0 plane spans 5.359 units of height —
 * 1 px = 0.002791 units. px(x, y) -> world((x - 540) * k, (960 - y) * k).
 */
const K = (2 * 10 * Math.tan((15 * Math.PI) / 180)) / H;
export const at = (x: number, y: number): [number, number, number] => [
  (x - W / 2) * K,
  (H / 2 - y) * K,
  0,
];

/** Soft contact shadow on the wall behind an object (screen space). */
const WallShadow: React.FC<{ x: number; y: number; w: number; h: number }> = ({
  x,
  y,
  w,
  h,
}) => (
  <div
    style={{
      position: "absolute",
      left: x - w / 2,
      top: y - h / 2,
      width: w,
      height: h,
      borderRadius: "50%",
      background:
        "radial-gradient(closest-side, rgba(40,40,45,0.38), rgba(40,40,45,0))",
      filter: "blur(14px)",
    }}
  />
);

/** Style frame at 58.6 s: fryer closed and switched on, finger on the button, globe spinning. */
export const AirFryerStyleFrame: React.FC = () => (
  <AbsoluteFill>
    <Img src={staticFile("airfryer/bg.png")} style={{ width: W, height: H }} />
    <WallShadow x={285} y={500} w={340} h={360} />
    <WallShadow x={880} y={455} w={330} h={330} />
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
    <Img
      src={staticFile("airfryer/person.png")}
      style={{ position: "absolute", inset: 0, width: W, height: H }}
    />
  </AbsoluteFill>
);
