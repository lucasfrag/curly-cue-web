// App.tsx
import { useRef, useEffect, useState } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

export default function App() {
  const mountRef = useRef<HTMLDivElement>(null);
  const [params, setParams] = useState({
    density: 1.0,
    scale: 1.0,
    curvature: 1.0,
  });

  useEffect(() => {
    const width = mountRef.current?.clientWidth || 800;
    const height = mountRef.current?.clientHeight || 600;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current?.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(0, 1, 2);
    scene.add(light);

    const ambient = new THREE.AmbientLight(0x404040);
    scene.add(ambient);

    camera.position.z = 3;

    // Placeholder: Add sample geometry
    const geometry = new THREE.TorusKnotGeometry(0.5, 0.15, 100, 16);
    const material = new THREE.MeshStandardMaterial({ color: 0xff7f50 });
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    const animate = () => {
      requestAnimationFrame(animate);
      mesh.rotation.y += 0.01;
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      mountRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div className="w-screen h-screen flex bg-zinc-900 text-white font-sans overflow-hidden">
      {/* Painel de Controle */}
      <div className="w-1/2 h-full p-8 flex flex-col gap-6 bg-zinc-950 shadow-lg">
        <h1 className="text-3xl font-bold mb-2">🎨 CurlyCue - Configuração</h1>

        <div className="space-y-4">
          <div>
            <label className="block mb-1 text-sm">Densidade</label>
            <input
              type="range"
              min="0.1"
              max="2"
              step="0.1"
              value={params.density}
              onChange={(e) => setParams({ ...params, density: parseFloat(e.target.value) })}
              className="w-full"
            />
            <p className="text-xs mt-1">Valor: {params.density.toFixed(1)}</p>
          </div>

          <div>
            <label className="block mb-1 text-sm">Escala</label>
            <input
              type="range"
              min="0.1"
              max="2"
              step="0.1"
              value={params.scale}
              onChange={(e) => setParams({ ...params, scale: parseFloat(e.target.value) })}
              className="w-full"
            />
            <p className="text-xs mt-1">Valor: {params.scale.toFixed(1)}</p>
          </div>

          <div>
            <label className="block mb-1 text-sm">Curvatura</label>
            <input
              type="range"
              min="0.1"
              max="2"
              step="0.1"
              value={params.curvature}
              onChange={(e) => setParams({ ...params, curvature: parseFloat(e.target.value) })}
              className="w-full"
            />
            <p className="text-xs mt-1">Valor: {params.curvature.toFixed(1)}</p>
          </div>

          <button
            className="mt-6 bg-emerald-600 hover:bg-emerald-700 text-white py-2 px-4 rounded-lg transition-all shadow"
            onClick={() => alert("Gerar Geometria ainda não implementado")}
          >
            🚀 Gerar Geometria
          </button>
        </div>
      </div>

      {/* Visualização 3D */}
      <div className="w-1/2 h-full relative">
        <div ref={mountRef} className="w-full h-full" />
      </div>
    </div>
  );
}
