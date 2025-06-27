import * as THREE from "three";

/**
 * Classe que representa um fio de cabelo simulado fisicamente
 */
export class HairStrand {
  points: THREE.Vector3[];
  prevPoints: THREE.Vector3[];
  segmentLength: number;
  gravity: THREE.Vector3;
  wind: THREE.Vector3;
  stiffness: number;

  constructor(points: THREE.Vector3[], segmentLength: number = 0.02, stiffness = 1.0) {
    this.points = points;
    this.prevPoints = points.map(p => p.clone());
    this.segmentLength = segmentLength;
    this.gravity = new THREE.Vector3(0, -0.00098, 0); // Gravidade suave
    this.wind = new THREE.Vector3(0.002, 0, 0); // Vento leve
    this.stiffness = stiffness;
  }

  update() {
    console.log("Atualizando strand...");
    // Integração Verlet: atualiza posições com base no movimento anterior
    for (let i = 1; i < this.points.length; i++) {
      const p = this.points[i];
      const prev = this.prevPoints[i];
      const velocity = p.clone().sub(prev);
      this.prevPoints[i] = p.clone();

      p.add(velocity);
      p.add(this.gravity);
      p.add(this.wind);
    }

    // Constrição de segmentos (manter distância fixa entre partículas)
    for (let i = 0; i < 3; i++) {
      for (let j = 1; j < this.points.length; j++) {
        const p1 = this.points[j - 1];
        const p2 = this.points[j];
        const delta = p2.clone().sub(p1);
        const dist = delta.length();
        const diff = (dist - this.segmentLength) / dist;

        const correction = delta.multiplyScalar(0.5 * this.stiffness * diff);

        if (j !== 1) p1.add(correction);
        p2.sub(correction);
      }
    }

    // Fixa a raiz do fio
    this.points[0].copy(this.prevPoints[0]);
  }
}

/**
 * Gerencia todos os fios no BufferGeometry
 */
export class HairSimulator {
  strands: HairStrand[] = [];
  geometry: THREE.BufferGeometry;
  strandLength: number;

  constructor(geometry: THREE.BufferGeometry, strandLength: number = 20) {
    this.geometry = geometry;
    this.strandLength = strandLength;

    const posAttr = geometry.getAttribute("position") as THREE.BufferAttribute;
    const positions = posAttr.array as Float32Array;

    for (let i = 0; i < positions.length; i += strandLength * 3) {
      const points: THREE.Vector3[] = [];
      for (let j = 0; j < strandLength; j++) {
        const x = positions[i + j * 3];
        const y = positions[i + j * 3 + 1];
        const z = positions[i + j * 3 + 2];
        points.push(new THREE.Vector3(x, y, z));
      }
      this.strands.push(new HairStrand(points));
    }
  }

  update() {
    this.strands.forEach(strand => strand.update());

    const posAttr = this.geometry.getAttribute("position") as THREE.BufferAttribute;
    const positions = posAttr.array as Float32Array;

    let index = 0;
    this.strands.forEach(strand => {
      strand.points.forEach(p => {
        positions[index++] = p.x;
        positions[index++] = p.y;
        positions[index++] = p.z;
      });
    });

    posAttr.needsUpdate = true;
  }

  setPhysicsParams(params: { gravity: THREE.Vector3; wind: THREE.Vector3; stiffness: number }) {
  this.strands.forEach(strand => {
    strand.gravity = params.gravity.clone();
    strand.wind = params.wind.clone();
    strand.stiffness = params.stiffness;
  });
}
}
