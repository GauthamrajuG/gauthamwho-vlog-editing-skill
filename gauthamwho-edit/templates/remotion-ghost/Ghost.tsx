import React, { useMemo } from "react";
import * as THREE from "three";

/**
 * A hooded, dark-robed figure for the Reel 29 walk-in scare. Local units:
 * the eye line sits at the origin, the hood is ~0.84 wide, the robe hangs to
 * y = -2 (the compositor dissolves it into smoke long before that).
 *
 * Built from one lathe profile (hood -> neck -> shoulders -> robe), with
 * cloth folds pushed in by layered sine noise that grows towards the hem,
 * a velvet-like sheen material, a black face void inside a thick hood brim,
 * and two slanted emissive eyes. The eyes' red light is a real point light
 * just in front of them, so it catches the inside of the brim.
 */

const PROFILE: [number, number][] = [
  [0.001, 0.6],
  [0.12, 0.585],
  [0.22, 0.54],
  [0.31, 0.45],
  [0.37, 0.32],
  [0.4, 0.16],
  [0.405, 0.0],
  [0.39, -0.16],
  [0.36, -0.29],
  [0.44, -0.38],
  [0.62, -0.47],
  [0.76, -0.6],
  [0.83, -0.8],
  [0.86, -1.1],
  [0.9, -1.5],
  [0.96, -2.0],
];

const useRobe = (dragX: number, dragY: number, phase: number) =>
  useMemo(() => {
    // smooth the hand-placed profile so the silhouette has no facets
    const pts = new THREE.SplineCurve(
      PROFILE.map(([r, y]) => new THREE.Vector2(r, y)),
    ).getPoints(120);
    const g = new THREE.LatheGeometry(pts, 160);
    const p = g.attributes.position as THREE.BufferAttribute;
    const v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i);
      const a = Math.atan2(v.z, v.x);
      // folds: none on the hood crown, soft on the hood sides, deep in the robe
      const robe = THREE.MathUtils.smoothstep(-v.y, 0.3, 1.2);
      const hood = THREE.MathUtils.smoothstep(-v.y, -0.45, 0.1) * 0.45;
      const amt = robe + hood;
      const f =
        0.05 * Math.sin(a * 6 + v.y * 1.7) +
        0.028 * Math.sin(a * 11 - v.y * 3.1 + 1.3) +
        0.014 * Math.sin(a * 23 + v.y * 5.3 + 0.4) +
        0.006 * Math.sin(a * 47 - v.y * 9.0 + 2.1);
      const k = 1 + (f * amt) / Math.max(0.2, Math.hypot(v.x, v.z));
      // hood leans forward over the face a little
      const lean = THREE.MathUtils.smoothstep(v.y, -0.1, 0.55) * 0.06;
      // the body trails its motion: nothing at the head, more and more towards
      // the hem (drag), with a travelling ripple running down the cloth (phase)
      const w = Math.pow(THREE.MathUtils.smoothstep(-v.y, 0.2, 2.0), 1.4);
      const ripple = 0.035 * Math.sin(v.y * 4.2 + phase) * w;
      p.setXYZ(
        i,
        v.x * k + dragX * w + ripple,
        v.y + dragY * w,
        v.z * k + lean + 0.5 * ripple,
      );
    }
    g.computeVertexNormals();
    return g;
  }, [dragX, dragY, phase]);

/** The thick brim around the face opening: a tube along an egg-shaped loop. */
const useBrim = () =>
  useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i < 64; i++) {
      const t = (i / 64) * Math.PI * 2;
      const egg = 1 + 0.12 * Math.sin(t); // a bit wider above the eyes
      pts.push(
        new THREE.Vector3(
          0.235 * Math.cos(t) * egg,
          0.3 * Math.sin(t) - 0.02,
          0.385 - 0.04 * Math.abs(Math.cos(t)),
        ),
      );
    }
    return new THREE.TubeGeometry(
      new THREE.CatmullRomCurve3(pts, true),
      128,
      0.035,
      12,
      true,
    );
  }, []);

const cloth = new THREE.MeshPhysicalMaterial({
  color: "#1c191e",
  roughness: 0.92,
  sheen: 1,
  sheenColor: new THREE.Color("#5e5664"),
  sheenRoughness: 0.55,
});

export const EYE_Z = 0.385;

export const Ghost: React.FC<{
  eyes: number;
  drag?: [number, number];
  phase?: number;
}> = ({ eyes, drag = [0, 0], phase = 0 }) => {
  const robe = useRobe(drag[0], drag[1], phase);
  const brim = useBrim();
  const eyeColor = useMemo(
    () => new THREE.Color("#ff3218").multiplyScalar(1.5 + 2.5 * eyes),
    [eyes],
  );
  return (
    <group>
      <mesh geometry={robe} material={cloth} />
      <mesh geometry={brim} material={cloth} />
      {/* the face: a black void just inside the brim */}
      <mesh position={[0, -0.02, 0.3]} scale={[0.24, 0.3, 0.07]}>
        <sphereGeometry args={[1, 48, 32]} />
        <meshBasicMaterial color="#000000" />
      </mesh>
      {[-1, 1].map((s) => (
        <mesh
          key={s}
          position={[s * 0.085, 0.02, EYE_Z]}
          rotation={[0, 0, s * 0.32]}
          scale={[0.036, 0.011, 0.02]}
        >
          <sphereGeometry args={[1, 32, 16]} />
          <meshBasicMaterial
            color={eyeColor}
            toneMapped={false}
            transparent
            opacity={Math.min(1, eyes * 1.5)}
          />
        </mesh>
      ))}
      <pointLight
        position={[0, -0.06, EYE_Z + 0.04]}
        color="#ff2410"
        intensity={0.45 * eyes}
        distance={0.36}
        decay={2}
      />
    </group>
  );
};
