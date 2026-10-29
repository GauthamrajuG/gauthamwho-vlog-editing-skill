import React from "react";
import { roundedBox } from "./shapes";

const SKIN = "#8a5435";
const Skin: React.FC = () => (
  <meshPhysicalMaterial
    color={SKIN}
    roughness={0.66}
    envMapIntensity={0.45}
    sheen={0.35}
    sheenColor="#e0a07a"
    sheenRoughness={0.7}
  />
);

/**
 * One finger as three phalanges; `curl` bends each joint forward (towards the
 * palm side, -z). Lengths follow real proportions (proximal > middle > tip).
 */
const Finger: React.FC<{
  x: number;
  y: number;
  len: number;
  r: number;
  curl: number;
  splay?: number;
}> = ({ x, y, len, r, curl, splay = 0 }) => {
  const [a, b, c] = [len * 0.44, len * 0.31, len * 0.25];
  return (
    <group position={[x, y, 0]} rotation={[-curl, 0, splay]}>
      <mesh position={[0, a / 2, 0]}>
        <capsuleGeometry args={[r, a, 8, 16]} />
        <Skin />
      </mesh>
      <group position={[0, a, 0]} rotation={[-curl * 1.15, 0, 0]}>
        <mesh position={[0, b / 2, 0]}>
          <capsuleGeometry args={[r * 0.94, b, 8, 16]} />
          <Skin />
        </mesh>
        <group position={[0, b, 0]} rotation={[-curl * 0.8, 0, 0]}>
          <mesh position={[0, c / 2, 0]}>
            <capsuleGeometry args={[r * 0.88, c, 8, 16]} />
            <Skin />
          </mesh>
        </group>
      </group>
    </group>
  );
};

const palm = roundedBox(0.28, 0.3, 0.1, 0.08, 0.035);

/**
 * A pressing hand, back of the hand facing the viewer: index finger straight,
 * the other three curled into the palm, thumb resting on the middle finger.
 * It ends at the wrist (a short, rounded cuff) — no arm: the hand pops in,
 * taps and pops out on its own. The origin is the index fingertip, so the
 * hand is placed by putting the origin on a button.
 */
export const Hand: React.FC = () => {
  // index: base y 0.15, length 0.3 -> tip at y = 0.15 + 0.3 + r
  const tipY = 0.15 + 0.3 + 0.035;
  return (
    <group position={[0.095, -tipY, 0]}>
      {/* wrist, ending in a clean rounded cuff */}
      <mesh position={[0, -0.24, 0]} scale={[1.12, 1, 0.74]}>
        <capsuleGeometry args={[0.105, 0.16, 8, 24]} />
        <Skin />
      </mesh>
      {/* palm */}
      <mesh geometry={palm}>
        <Skin />
      </mesh>
      {/* knuckles */}
      {[-0.095, -0.032, 0.032, 0.093].map((x, i) => (
        <mesh key={i} position={[x, 0.145, 0.012]}>
          <sphereGeometry args={[0.039, 16, 12]} />
          <Skin />
        </mesh>
      ))}
      <Finger x={-0.095} y={0.15} len={0.3} r={0.035} curl={0} splay={0.04} />
      <Finger x={-0.032} y={0.15} len={0.31} r={0.036} curl={1.25} />
      <Finger x={0.032} y={0.145} len={0.29} r={0.035} curl={1.3} />
      <Finger
        x={0.093}
        y={0.135}
        len={0.23}
        r={0.031}
        curl={1.35}
        splay={-0.05}
      />
      {/* thumb, folded across the curled fingers */}
      <group position={[-0.12, -0.03, -0.02]} rotation={[-0.5, 0, 1.05]}>
        <mesh position={[0, 0.06, 0]}>
          <capsuleGeometry args={[0.036, 0.11, 8, 16]} />
          <Skin />
        </mesh>
        <group position={[0, 0.12, 0]} rotation={[-0.6, 0, 0.3]}>
          <mesh position={[0, 0.05, 0]}>
            <capsuleGeometry args={[0.033, 0.08, 8, 16]} />
            <Skin />
          </mesh>
        </group>
      </group>
    </group>
  );
};
