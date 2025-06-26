import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { MTLLoader } from "three/examples/jsm/loaders/MTLLoader";
import "./App.css";

type Preset = {
  name: string;
  guidePath: string;
  scalpPath: string;
  groupingCSV: string;
};

const presets: Preset[] = [
  {
    name: "Side Swatch",
    guidePath: "data/guide_strands/sideSwatchDroopSequence/70.obj",
    scalpPath: "data/scalp_clouds/sideSwatchScalp.obj",
    groupingCSV:
      "data/matching_csvs/sideSwatchGuides-sideSwatchScalp-groupingsr30.csv",
  },
];

export default function App() {
  const sceneRef = useRef<THREE.Scene>();
  const hairRef = useRef<THREE.Object3D>();
  const scalpRef = useRef<THREE.Object3D>();
  const containerRef = useRef<HTMLDivElement>(null);

  const [selectedPreset, setSelectedPreset] = useState(presets[0]);
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState("Aguardando geração...");
  const [groupingRadius, setGroupingRadius] = useState("30");
  const [color, setColor] = useState("#000000");
  const [params, setParams] = useState({ curliness: 0.5, length: 1.0, density: 1.0 });
  const [showScalp, setShowScalp] = useState(true);

  const [windOn, setWindOn] = useState(true);
  const [windStrength, setWindStrength] = useState(0.1);
  const [windSpeed, setWindSpeed] = useState(1.0);

  const originalHairGeometries = useRef<{ mesh: THREE.Mesh; original: Float32Array }[]>([]);

  useEffect(() => {
    if (!containerRef.current) return;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(60, 1, 0.01, 100);
    camera.position.set(0, 0.2, 1.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputEncoding = THREE.sRGBEncoding;
    containerRef.current.innerHTML = "";
    containerRef.current.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.rotateSpeed = 0.5;

    scene.background = new THREE.Color("#eef2f3");

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
    dirLight.position.set(2, 2, 2);
    scene.add(ambientLight, dirLight);

    const clock = new THREE.Clock();

    const centerScene = () => {
      const group = new THREE.Group();
      if (hairRef.current) group.add(hairRef.current.clone());
      if (scalpRef.current) group.add(scalpRef.current.clone());

      const box = new THREE.Box3().setFromObject(group);
      const center = new THREE.Vector3();
      box.getCenter(center);

      controls.target.copy(center);
      camera.position.copy(center.clone().add(new THREE.Vector3(0, 0.2, 1.2)));
      camera.lookAt(center);
    };

    const animate = () => {
      requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      if (windOn && originalHairGeometries.current.length > 0) {
        originalHairGeometries.current.forEach(({ mesh, original }) => {
          const geometry = mesh.geometry as THREE.BufferGeometry;
          const positionAttr = geometry.attributes.position as THREE.BufferAttribute;
          const pos = positionAttr.array as Float32Array;

          for (let i = 0; i < pos.length; i += 3) {
            const ox = original[i];
            const oy = original[i + 1];
            const oz = original[i + 2];

            const offset = (oy + oz) * 2.0;
            pos[i] = ox + Math.sin(elapsed * windSpeed + offset) * windStrength;
            pos[i + 1] = oy;
            pos[i + 2] = oz;
          }

          positionAttr.needsUpdate = true;
        });
      }

      controls.update();
      renderer.render(scene, camera);
    };

    animate();
    setTimeout(centerScene, 300);

    loadHairModel(scene);
    if (showScalp) loadScalpModel(scene);

    return () => {
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, [selectedPreset]);

  useEffect(() => {
    if (!sceneRef.current) return;
    const scene = sceneRef.current;
    const scalp = scene.getObjectByName("ScalpModel");
    if (scalp && !showScalp) scene.remove(scalp);
    else if (!scalp && showScalp) loadScalpModel(scene);
  }, [showScalp, selectedPreset]);

  const handleGenerate = async () => {
    setLoading(true);
    setLog("Enviando solicitação para o backend...");
    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          guidePath: selectedPreset.guidePath,
          scalpPath: selectedPreset.scalpPath,
          groupingCSV: selectedPreset.groupingCSV.replace(/r\d+/, `r${groupingRadius}`),
          outputPath: "output/strands.obj",
          ...params,
          color: color,
        }),
      });
      const data = await response.json();
      setLog(`Geração concluída: ${data.message || "OK"}`);
    } catch (error) {
      setLog("Erro ao gerar cabelo.");
    } finally {
      setLoading(false);
    }

    if (sceneRef.current) loadHairModel(sceneRef.current);
  };

  const loadHairModel = (scene: THREE.Scene) => {
    const mtlLoader = new MTLLoader();
    mtlLoader.setPath("http://localhost:8000/output/");
    mtlLoader.load("strands.mtl", (materials) => {
      materials.preload();

      const objLoader = new OBJLoader();
      objLoader.setMaterials(materials);
      objLoader.setPath("http://localhost:8000/output/");
      objLoader.load("strands.obj", (obj) => {
        obj.scale.set(0.05, 0.05, 0.05);

        const existing = scene.getObjectByName("HairModel");
        if (existing) scene.remove(existing);

        obj.name = "HairModel";
        hairRef.current = obj;
        scene.add(obj);

        originalHairGeometries.current = [];

        obj.traverse((child) => {
          const geometry = (child as any).geometry as THREE.BufferGeometry | undefined;

          if (geometry && geometry.attributes?.position) {
            const position = geometry.attributes.position as THREE.BufferAttribute;

            geometry.setAttribute("position", new THREE.BufferAttribute(position.array, 3));
            geometry.attributes.position.setUsage(THREE.DynamicDrawUsage);

            originalHairGeometries.current.push({
              mesh: child as THREE.Mesh,
              original: position.array.slice() as Float32Array,
            });

            console.log("Adicionado segmento com", position.count, "vértices");
          }
        });
      });
    });
  };

  const loadScalpModel = (scene: THREE.Scene) => {
    const loader = new OBJLoader();
    loader.setPath("http://localhost:8000/");
    loader.load(selectedPreset.scalpPath, (obj) => {
      obj.name = "ScalpModel";
      obj.scale.set(0.05, 0.05, 0.05);

      const existing = scene.getObjectByName("ScalpModel");
      if (existing) scene.remove(existing);

      scalpRef.current = obj;
      scene.add(obj);
    });
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <h1>Simulador de Cabelo Cacheado</h1>
        <p className="description">Explore diferentes configurações de cabelo. Ajuste os parâmetros abaixo e visualize os resultados em tempo real.</p>

        <label htmlFor="preset">Modelo base (preset):</label>
        <select id="preset" value={selectedPreset.name} onChange={(e) => setSelectedPreset(presets.find((p) => p.name === e.target.value)!)} >
          {presets.map((preset) => (
            <option key={preset.name} value={preset.name}>{preset.name}</option>
          ))}
        </select>

        <label htmlFor="groupingRadius" title="Agrupamento controla o quão agrupados os fios estão (mechas).">Agrupamento (rX):</label>
        <select id="groupingRadius" value={groupingRadius} onChange={(e) => setGroupingRadius(e.target.value)} >
          <option value="1">r1 - Fios mais soltos</option>
          <option value="2">r2</option>
          <option value="5">r5</option>
          <option value="10">r10</option>
          <option value="20">r20</option>
          <option value="30">r30 - Mechas bem agrupadas</option>
        </select>

        <div className="slider-group">
          <label htmlFor="curliness">Curliness: {params.curliness.toFixed(2)}</label>
          <input type="range" id="curliness" min={0} max={1} step={0.01} value={params.curliness} onChange={(e) => setParams({ ...params, curliness: parseFloat(e.target.value) })} />

          <label htmlFor="length">Length: {params.length.toFixed(2)}</label>
          <input type="range" id="length" min={0.1} max={2.0} step={0.1} value={params.length} onChange={(e) => setParams({ ...params, length: parseFloat(e.target.value) })} />

          <label htmlFor="density">Density: {params.density.toFixed(2)}</label>
          <input type="range" id="density" min={0.1} max={2.0} step={0.1} value={params.density} onChange={(e) => setParams({ ...params, density: parseFloat(e.target.value) })} />
        </div>

        <label htmlFor="color">Cor do cabelo:</label>
        <input type="color" id="color" value={color} onChange={(e) => setColor(e.target.value)} />

        <label><input type="checkbox" checked={showScalp} onChange={(e) => setShowScalp(e.target.checked)} /> Mostrar couro cabeludo</label>


        <button onClick={handleGenerate} disabled={loading}>
          {loading ? "Gerando..." : "Gerar Cabelo"}
        </button>

        <a
          href="http://localhost:8000/output/strands.obj"
          download="cabelo_gerado.obj"
          className="download-button"
        >
          ⬇️ Baixar .obj
        </a>

        {loading && <div className="loader"></div>}
        <p className="log">{log}</p>
      </div>

      <div className="preview" ref={containerRef}></div>
    </div>
  );
}
