import React, { useLayoutEffect } from "react";
import * as THREE from "three";
import { useThree } from "@react-three/fiber";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

/**
 * Studio reflections: a soft room environment for every material to reflect
 * (black plastic gets its sheen, the silver window frame and glass their
 * highlights), plus a key light from top-left, a cool rim from the right and
 * a fill. Without an environment, metal renders black.
 */
export const Studio: React.FC = () => {
  const { gl, scene } = useThree();
  useLayoutEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = 0.85;
    return () => {
      scene.environment = null;
      env.dispose();
      pmrem.dispose();
    };
  }, [gl, scene]);
  return (
    <>
      <ambientLight intensity={0.25} />
      <directionalLight position={[-4, 6, 6]} intensity={2.2} color="#fff4e6" />
      <directionalLight position={[5, 2, -4]} intensity={1.2} color="#cfe3ff" />
      <directionalLight position={[2, -3, 5]} intensity={0.5} color="#fff2e0" />
    </>
  );
};
