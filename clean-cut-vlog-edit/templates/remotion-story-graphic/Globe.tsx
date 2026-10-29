import React, { useMemo } from "react";
import * as THREE from "three";
import { geoEquirectangular, geoGraticule10, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import land50 from "world-atlas/land-50m.json";

/**
 * Earth texture drawn from Natural Earth land shapes (world-atlas, public
 * domain): deep ocean, land shaded from green tropics to dry mid-latitudes,
 * ice at the poles. Equirectangular so it wraps a sphere exactly.
 */
const useEarthTexture = () =>
  useMemo(() => {
    const W = 2048;
    const H = 1024;
    const c = document.createElement("canvas");
    c.width = W;
    c.height = H;
    const ctx = c.getContext("2d")!;
    const ocean = ctx.createLinearGradient(0, 0, 0, H);
    ocean.addColorStop(0, "#0b2e6b");
    ocean.addColorStop(0.5, "#1257b0");
    ocean.addColorStop(1, "#0b2e6b");
    ctx.fillStyle = ocean;
    ctx.fillRect(0, 0, W, H);

    const proj = geoEquirectangular()
      .scale(W / (2 * Math.PI))
      .translate([W / 2, H / 2]);
    const path = geoPath(proj, ctx);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const topo = land50 as any;
    const land = feature(topo, topo.objects.land);
    const landFill = ctx.createLinearGradient(0, 0, 0, H);
    landFill.addColorStop(0.0, "#e8f0f2");
    landFill.addColorStop(0.12, "#7fae6a");
    landFill.addColorStop(0.3, "#b9a46a");
    landFill.addColorStop(0.45, "#3f9a4a");
    landFill.addColorStop(0.55, "#2f8a40");
    landFill.addColorStop(0.7, "#b39a62");
    landFill.addColorStop(0.88, "#8fb07a");
    landFill.addColorStop(1.0, "#f2f6f8");
    ctx.beginPath();
    path(land);
    ctx.fillStyle = landFill;
    ctx.fill();
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = "rgba(255,255,255,0.18)";
    ctx.stroke();
    ctx.beginPath();
    path(geoGraticule10());
    ctx.lineWidth = 0.6;
    ctx.strokeStyle = "rgba(255,255,255,0.05)";
    ctx.stroke();

    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    return t;
  }, []);

/** Fresnel rim glow, drawn on the inside of a slightly larger sphere. */
const atmosphereMaterial = () =>
  new THREE.ShaderMaterial({
    transparent: true,
    blending: THREE.AdditiveBlending,
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: { color: { value: new THREE.Color("#5fb4ff") } },
    vertexShader: `
      varying vec3 vNormal;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      uniform vec3 color;
      varying vec3 vNormal;
      void main() {
        float i = pow(0.62 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 3.0);
        gl_FragColor = vec4(color, 1.0) * i * 0.9;
      }`,
  });

/**
 * The Earth. `spin` is the rotation in radians around its own (23.4° tilted)
 * axis; increasing it turns the surface left to right as seen from the front.
 */
export const Globe: React.FC<{ spin: number; radius?: number }> = ({
  spin,
  radius = 1,
}) => {
  const map = useEarthTexture();
  const atmo = useMemo(atmosphereMaterial, []);
  return (
    <group rotation={[0, 0, -0.41]}>
      <mesh rotation={[0, spin, 0]}>
        <sphereGeometry args={[radius, 96, 64]} />
        <meshStandardMaterial map={map} roughness={0.75} metalness={0.02} />
      </mesh>
      <mesh scale={1.07} material={atmo}>
        <sphereGeometry args={[radius, 64, 48]} />
      </mesh>
    </group>
  );
};
