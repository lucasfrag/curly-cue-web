import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { MTLLoader } from "three/examples/jsm/loaders/MTLLoader";
import "./App.css";
import { HairSimulator } from "./HairPhysics";

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
  const simulatorRef = useRef<HairSimulator | null>(null);
  const sceneRef = useRef<THREE.Scene>();
  const hairRef = useRef<THREE.Object3D>();
  const scalpRef = useRef<THREE.Object3D>();
  const containerRef = useRef<HTMLDivElement>(null);
  const originalHairGeometries = useRef<{ mesh: THREE.Mesh; original: Float32Array }[]>([]);

  const [selectedPreset, setSelectedPreset] = useState(presets[0]);
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState("Aguardando geração...");
  const [groupingRadius, setGroupingRadius] = useState("30");
  const [color, setColor] = useState("#000000");
  const [params, setParams] = useState({ curliness: 0.5, length: 1.0, density: 1.0 });
  const [showScalp, setShowScalp] = useState(true);

  const [physicsOn, setPhysicsOn] = useState(false);
  const [gravityStrength, setGravityStrength] = useState(0.01);
  const [windStrength, setWindStrength] = useState(0.01);
  const [stiffness, setStiffness] = useState(0.2);

  const physicsOnRef = useRef(physicsOn);
  const gravityRef = useRef(gravityStrength);
  const windRef = useRef(windStrength);
  const stiffnessRef = useRef(stiffness);


  useEffect(() => {
    physicsOnRef.current = physicsOn;
  }, [physicsOn]);

  useEffect(() => {
    gravityRef.current = gravityStrength;
  }, [gravityStrength]);

  useEffect(() => {
    windRef.current = windStrength;
  }, [windStrength]);

  useEffect(() => {
    stiffnessRef.current = stiffness;
  }, [stiffness]);


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
      controls.update();

      if (simulatorRef.current && physicsOnRef.current) {

        console.log("Física está ativa. Atualizando...");
        simulatorRef.current.setPhysicsParams({
          gravity: new THREE.Vector3(0, -gravityRef.current, 0),
          wind: new THREE.Vector3(windRef.current, 0, 0),
          stiffness: stiffnessRef.current,
        });
        simulatorRef.current.update();
      }

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
    const timestamp = Date.now();
    mtlLoader.setPath("http://localhost:8000/output/");
    mtlLoader.load(`strands.mtl?t=${timestamp}`, (materials) => {
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
          if (!("geometry" in child)) return;

          const mesh = child as THREE.Mesh;
          const geometry = mesh.geometry as THREE.BufferGeometry;

          if (!geometry || !geometry.attributes?.position) return;

          geometry.attributes.position.setUsage(THREE.DynamicDrawUsage);


          simulatorRef.current = new HairSimulator(geometry);
          simulatorRef.current.setPhysicsParams({
            gravity: new THREE.Vector3(0, -gravityStrength, 0),
            wind: new THREE.Vector3(windStrength, 0, 0),
            stiffness: stiffness,
          });


          const position = geometry.attributes.position as THREE.BufferAttribute;
          geometry.setAttribute("position", new THREE.BufferAttribute(position.array, 3));

          originalHairGeometries.current.push({
            mesh: mesh,
            original: position.array.slice() as Float32Array,
          });

          console.log("Adicionado segmento com", position.count, "vértices");
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
  <h1>💇 Curly Hair Simulator</h1>
  <p className="description">
    Explore different hair configurations. Adjust the parameters below and visualize the results in real time.
  </p>

  <div className="card">
    <h3>🧬 Model</h3>
    <label>Base model (preset):</label>
    <select value={selectedPreset.name} onChange={(e) => setSelectedPreset(presets.find(p => p.name === e.target.value)!)} >
      {presets.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
    </select>

    <label>Clumping (rX):</label>
    <select value={groupingRadius} onChange={(e) => setGroupingRadius(e.target.value)} >
      <option value="1">r1 - Loose strands</option>
      <option value="2">r2</option>
      <option value="5">r5</option>
      <option value="10">r10</option>
      <option value="20">r20</option>
      <option value="30">r30 - Tight groups</option>
    </select>

    <label>Hair color:</label>
    <input type="color" value={color} onChange={(e) => setColor(e.target.value)} />

    <label>
      <input type="checkbox" checked={showScalp} onChange={(e) => setShowScalp(e.target.checked)} />
      Show scalp
    </label>
  </div>

  <div className="card">
    <h3>🎛️ Parameters</h3>
    <div className="slider-group">
      <label>🌀 Curliness: {params.curliness.toFixed(2)}</label>
      <input type="range" min={0} max={1} step={0.01} value={params.curliness} onChange={(e) => setParams({ ...params, curliness: parseFloat(e.target.value) })} />

      <label>📏 Length: {params.length.toFixed(2)}</label>
      <input type="range" min={0.1} max={2.0} step={0.1} value={params.length} onChange={(e) => setParams({ ...params, length: parseFloat(e.target.value) })} />

      <label>🧵 Density: {params.density.toFixed(2)}</label>
      <input type="range" min={0.1} max={2.0} step={0.1} value={params.density} onChange={(e) => setParams({ ...params, density: parseFloat(e.target.value) })} />
    </div>
  </div>
  <div className="card">
    <h3>⚙️ Actions</h3>
    <button onClick={handleGenerate} disabled={loading}>
      {loading ? "⏳ Generating..." : "✨ Generate Hair"}
    </button>

    <a href="http://localhost:8000/output/strands.obj" download="generated_hair.obj" className="download-button">
      ⬇️ Download .obj
    </a>

    {loading && <div className="loader"></div>}
    <p className="log">{log}</p>
  </div>


  <div className="card">
    <h3>🌬️ Physics</h3>

    <label>🌎 Gravity: {gravityStrength.toFixed(3)}</label>
    <input type="range" min={0} max={0.1} step={0.001} value={gravityStrength} onChange={(e) => setGravityStrength(parseFloat(e.target.value))} />

    <label>💨 Wind: {windStrength.toFixed(3)}</label>
    <input type="range" min={0} max={0.1} step={0.001} value={windStrength} onChange={(e) => setWindStrength(parseFloat(e.target.value))} />

    <label>🧱 Stiffness: {stiffness.toFixed(2)}</label>
    <input type="range" min={0} max={1} step={0.01} value={stiffness} onChange={(e) => setStiffness(parseFloat(e.target.value))} />

    <button
      onClick={() => setPhysicsOn(!physicsOn)}
      style={{ backgroundColor: physicsOn ? "#c0392b" : "#27ae60", marginBottom: "10px" }}
    >
      {physicsOn ? "🛑 Disable Physics" : "▶️ Enable Physics"}
    </button>

    <button
      onClick={() => {
        setPhysicsOn(false);
        if (sceneRef.current) {
          const scene = sceneRef.current;
          const hair = scene.getObjectByName("HairModel");
          const scalp = scene.getObjectByName("ScalpModel");
          if (hair) scene.remove(hair);
          if (scalp) scene.remove(scalp);
          loadHairModel(scene);
          if (showScalp) loadScalpModel(scene);
          setLog("Scene reset.");
        }
      }}
      style={{ backgroundColor: "#7f8c8d" }}
    >
      ♻️ Reset Scene
    </button>
  </div>



</div>


      <div className="preview" ref={containerRef}></div>
    </div>
  );
}
