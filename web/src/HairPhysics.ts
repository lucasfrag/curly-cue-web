import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import "./App.css";

type AnimationType =
  | "pendulum" | "spiral" | "noise" | "breeze" | "wave" | "pulse" | "chaos"
  | "ripple" | "zigzag" | "flutter" | "twist" | "fountain";

class HairSimulator {
  group: THREE.Group;
  hairs: {
    geometry: THREE.BufferGeometry;
    material: THREE.LineBasicMaterial;
    line: THREE.Line;
    baseAngle: number;
    current: THREE.Vector3[];
  }[] = [];

  time = 0;
  waveSpeed = 2.0;
  waveHeight = 0.02;
  physicsEnabled = false;
  animationType: AnimationType = "pendulum";

  constructor({ points }: { points: number[][][] }, scene: THREE.Scene) {
    this.group = new THREE.Group();

    for (const strand of points) {
      const current = strand.map(([x, y, z]) => new THREE.Vector3(x, y, z));

      const geometry = new THREE.BufferGeometry();
      const vertices = new Float32Array(current.length * 3);
      current.forEach((v, i) => {
        vertices[i * 3] = v.x;
        vertices[i * 3 + 1] = v.y;
        vertices[i * 3 + 2] = v.z;
      });
      geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));

      const material = new THREE.LineBasicMaterial({ color: 0x000000 });
      const line = new THREE.Line(geometry, material);
      this.group.add(line);

      const baseAngle = Math.random() * Math.PI * 2;
      this.hairs.push({ geometry, material, line, current, baseAngle });
    }

    scene.add(this.group);
  }

  setPhysicsEnabled(enabled: boolean) {
    this.physicsEnabled = enabled;
  }

  setAnimationType(type: AnimationType) {
    this.animationType = type;
  }

  update() {
    if (!this.physicsEnabled) return;
    this.time += 0.016; // assume ~60fps

    for (const strand of this.hairs) {
      const { geometry, current, baseAngle } = strand;
      const posAttr = geometry.getAttribute("position") as THREE.BufferAttribute;

      for (let i = 1; i < current.length; i++) {
        const phase = this.time * this.waveSpeed + i * 0.2 + baseAngle;
        let offsetX = 0, offsetZ = 0;

        switch (this.animationType) {
          case "pendulum":
            offsetX = Math.sin(phase) * this.waveHeight * (i / current.length);
            break;

          case "spiral":
            const angle = Math.sin(phase) * 0.05;
            offsetX = Math.cos(angle) * this.waveHeight * (i / current.length);
            offsetZ = Math.sin(angle) * this.waveHeight * (i / current.length);
            break;

          case "noise":
            offsetX = (Math.random() - 0.5) * 0.004;
            offsetZ = (Math.random() - 0.5) * 0.004;
            break;

          case "breeze":
            offsetX = Math.sin(phase * 0.5) * 0.01 * (1 - i / current.length);
            break;

          case "wave":
            offsetZ = Math.sin(phase) * this.waveHeight * 0.5;
            break;

          case "pulse":
            const scale = 1 + Math.sin(phase * 3) * 0.1;
            current[i].x *= scale;
            current[i].z *= scale;
            break;

          case "chaos":
            offsetX = Math.sin(phase) * this.waveHeight * 0.5 + (Math.random() - 0.5) * 0.01;
            offsetZ = Math.cos(phase) * this.waveHeight * 0.5 + (Math.random() - 0.5) * 0.01;
            break;

          case "ripple":
            const rippleFreq = 3;
            const rippleDecay = 0.5;
            offsetX = Math.sin(phase * rippleFreq) * this.waveHeight * Math.exp(-i * rippleDecay);
            offsetZ = Math.cos(phase * rippleFreq) * this.waveHeight * Math.exp(-i * rippleDecay);
            break;


          case "zigzag":
            offsetX = (i % 2 === 0 ? 1 : -1) * this.waveHeight * Math.sin(phase * 2);
            break;


          case "flutter":
            offsetX = Math.sin(phase * 10) * 0.003;
            offsetZ = Math.cos(phase * 12) * 0.003;
            break;

          case "twist":
            offsetX = Math.sin(i * 0.3 + phase) * 0.01;
            offsetZ = Math.cos(i * 0.3 + phase) * 0.01;
            break;


          case "fountain":
            offsetX = Math.sin(phase + i * 0.1) * this.waveHeight * (1 - i / current.length);
            current[i].y += Math.abs(Math.sin(phase + i * 0.2)) * 0.001;
            break;

        }

        current[i].x += offsetX;
        current[i].z += offsetZ;
        posAttr.setXYZ(i, current[i].x, current[i].y, current[i].z);
      }

      posAttr.needsUpdate = true;
    }
  }
}

export { HairSimulator };