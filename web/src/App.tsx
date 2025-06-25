import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
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
    groupingCSV: "data/matching_csvs/sideSwatchGuides-sideSwatchScalp-groupingsr30.csv",
  },
];

export default function App() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedPreset, setSelectedPreset] = useState(presets[0]);
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState("Aguardando geração...");

  const [params, setParams] = useState({
    curliness: 0.5,
    length: 1.0,
    density: 1.0,
  });

  useEffect(() => {
    if (!containerRef.current) return;

    const scene = new THREE.Scene();
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

    const loader = new OBJLoader();
    let hairObject: THREE.Group;

    loader.load(
      "http://localhost:8000/output/strands.obj",
      (obj) => {
        hairObject = obj;
        hairObject.scale.set(0.05, 0.05, 0.05);

        const box = new THREE.Box3().setFromObject(hairObject);
        const center = new THREE.Vector3();
        box.getCenter(center);
        hairObject.position.sub(center);

        scene.add(hairObject);
      },
      undefined,
      (err) => {
        console.error("Erro ao carregar .obj", err);
        setLog("Erro ao carregar o modelo 3D.");
      }
    );

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, [selectedPreset]);

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
          groupingCSV: selectedPreset.groupingCSV,
          outputPath: "output/strands.obj",
          ...params,
        }),
      });
      const data = await response.json();
      setLog(`Geração concluída: ${data.message || "OK"}`);
    } catch (error) {
      setLog("Erro ao gerar cabelo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <h1>Gerador de Cabelo</h1>

        <label htmlFor="preset">Preset:</label>
        <select
          id="preset"
          value={selectedPreset.name}
          onChange={(e) =>
            setSelectedPreset(presets.find((p) => p.name === e.target.value)!)
          }
        >
          {presets.map((preset) => (
            <option key={preset.name} value={preset.name}>
              {preset.name}
            </option>
          ))}
        </select>

        <div className="slider-group">
          <label htmlFor="curliness">Curliness: {params.curliness.toFixed(2)}</label>
          <input
            type="range"
            id="curliness"
            min={0}
            max={1}
            step={0.01}
            value={params.curliness}
            onChange={(e) =>
              setParams({ ...params, curliness: parseFloat(e.target.value) })
            }
          />

          <label htmlFor="length">Length: {params.length.toFixed(2)}</label>
          <input
            type="range"
            id="length"
            min={0.1}
            max={2.0}
            step={0.1}
            value={params.length}
            onChange={(e) =>
              setParams({ ...params, length: parseFloat(e.target.value) })
            }
          />

          <label htmlFor="density">Density: {params.density.toFixed(2)}</label>
          <input
            type="range"
            id="density"
            min={0.1}
            max={2.0}
            step={0.1}
            value={params.density}
            onChange={(e) =>
              setParams({ ...params, density: parseFloat(e.target.value) })
            }
          />
        </div>

        <button onClick={handleGenerate} disabled={loading}>
          {loading ? "Gerando..." : "Gerar Cabelo"}
        </button>

        {loading && <div className="loader"></div>}

        <p className="log">{log}</p>
      </div>

      <div className="preview" ref={containerRef}></div>
    </div>
  );
}
