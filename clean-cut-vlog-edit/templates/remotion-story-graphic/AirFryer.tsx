import React, { useMemo } from "react";
import * as THREE from "three";
import { roundedBox, roundedPlane } from "./shapes";

/** A soft diagonal reflection streak for the drawer's smoked glass. */
const useGlassTexture = () =>
  useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 256;
    c.height = 160;
    const ctx = c.getContext("2d")!;
    const base = ctx.createLinearGradient(0, 0, 0, 160);
    base.addColorStop(0, "#2a2d33");
    base.addColorStop(1, "#0e0f12");
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, 256, 160);
    const streak = ctx.createLinearGradient(40, 0, 150, 160);
    streak.addColorStop(0.3, "rgba(255,255,255,0)");
    streak.addColorStop(0.45, "rgba(255,255,255,0.22)");
    streak.addColorStop(0.55, "rgba(255,255,255,0.05)");
    streak.addColorStop(0.62, "rgba(255,255,255,0.14)");
    streak.addColorStop(0.75, "rgba(255,255,255,0)");
    ctx.fillStyle = streak;
    ctx.fillRect(0, 0, 256, 160);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, []);

const useDisplayTexture = () =>
  useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 256;
    c.height = 96;
    const ctx = c.getContext("2d")!;
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, 256, 96);
    ctx.fillStyle = "#ff7a1a";
    ctx.font = "bold 74px 'Courier New', monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("200", 128, 52);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, []);

/** Where the power button sits, in the fryer's own space (for placing the hand). */
export const BUTTON: [number, number, number] = [0.27, 0.43, 0.5];

/**
 * The creator's air fryer (black, slightly taller than wide): matte body,
 * glossy control strip on top-front with the orange "200" display and a round
 * power button, and a separate drawer — grey front, big smoked window in a
 * silver frame, chunky handle, basket behind — that slides along z.
 *
 * trayIn: 0 = drawer pulled out towards the viewer, 1 = closed.
 * on:     0..1 display + button light.
 * press:  0..1 how far the power button is pushed in.
 */
export const AirFryer: React.FC<{
  trayIn: number;
  on: number;
  press: number;
}> = ({ trayIn, on, press }) => {
  const g = useMemo(
    () => ({
      body: roundedBox(1.0, 1.24, 0.98, 0.17, 0.06),
      strip: roundedPlane(0.86, 0.22, 0.06),
      seam: roundedPlane(0.92, 0.78, 0.09),
      front: roundedBox(0.88, 0.74, 0.08, 0.08, 0.025),
      trim: roundedPlane(0.74, 0.46, 0.08),
      glass: roundedPlane(0.68, 0.4, 0.065),
      handle: roundedBox(0.42, 0.13, 0.2, 0.06, 0.03),
      basket: roundedBox(0.8, 0.6, 0.82, 0.06, 0.02),
    }),
    [],
  );
  const display = useDisplayTexture();
  const glass = useGlassTexture();
  const slide = (1 - trayIn) * 0.9;

  return (
    <group>
      <mesh geometry={g.body}>
        <meshPhysicalMaterial
          color="#141416"
          roughness={0.5}
          metalness={0.1}
          clearcoat={0.25}
          clearcoatRoughness={0.5}
        />
      </mesh>
      {/* glossy control strip */}
      <mesh geometry={g.strip} position={[0, 0.43, 0.491]}>
        <meshPhysicalMaterial
          color="#060607"
          roughness={0.08}
          metalness={0.25}
          clearcoat={1}
        />
      </mesh>
      <mesh position={[-0.14, 0.43, 0.493]}>
        <planeGeometry args={[0.3, 0.11]} />
        <meshStandardMaterial
          map={display}
          emissiveMap={display}
          emissive="#ff7a1a"
          emissiveIntensity={0.3 + on * 2.4}
          roughness={0.3}
        />
      </mesh>
      <group position={[BUTTON[0], BUTTON[1], 0.497 - press * 0.014]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.058, 0.062, 0.022, 48]} />
          <meshPhysicalMaterial
            color="#1c1c20"
            roughness={0.25}
            clearcoat={1}
          />
        </mesh>
        <mesh position={[0, 0, 0.0115]}>
          <ringGeometry args={[0.034, 0.045, 48]} />
          <meshStandardMaterial
            color="#ff8a2a"
            emissive="#ff6a10"
            emissiveIntensity={0.2 + on * 3.2}
          />
        </mesh>
      </group>
      {/* the opening the drawer sits in */}
      <mesh geometry={g.seam} position={[0, -0.17, 0.4905]}>
        <meshStandardMaterial color="#050505" roughness={0.9} />
      </mesh>
      {/* drawer: slides out along z */}
      <group position={[0, -0.17, 0.47 + slide]}>
        <mesh geometry={g.front}>
          <meshPhysicalMaterial
            color="#232327"
            roughness={0.38}
            metalness={0.2}
            clearcoat={0.6}
          />
        </mesh>
        <mesh geometry={g.trim} position={[0, 0.06, 0.043]}>
          <meshStandardMaterial
            color="#d2d3d8"
            metalness={1}
            roughness={0.22}
          />
        </mesh>
        <mesh geometry={g.glass} position={[0, 0.06, 0.045]}>
          <meshPhysicalMaterial
            map={glass}
            roughness={0.05}
            metalness={0.1}
            clearcoat={1}
          />
        </mesh>
        <mesh geometry={g.handle} position={[0, -0.29, 0.12]}>
          <meshPhysicalMaterial
            color="#0d0d0f"
            roughness={0.22}
            clearcoat={0.9}
          />
        </mesh>
        <mesh geometry={g.basket} position={[0, 0.0, -0.46]}>
          <meshStandardMaterial
            color="#2a2a2e"
            roughness={0.6}
            metalness={0.3}
          />
        </mesh>
      </group>
    </group>
  );
};
