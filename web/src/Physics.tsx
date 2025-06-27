import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import "./App.css";
import { HairSimulator } from "./HairPhysics";

export default function App() {
  const containerRef = useRef<HTMLDivElement>(null);
  const simulatorRef = useRef<HairSimulator | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const [animationType, setAnimationType] = useState<AnimationType>("pendulum");

  const [physicsOn, setPhysicsOn] = useState(false);
  const [gravityStrength, setGravityStrength] = useState(0.01);
  const [windStrength, setWindStrength] = useState(0.01);
  const [stiffness, setStiffness] = useState(0.2);
  const [damping, setDamping] = useState(0.95);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;
    const aspect = width / height;

    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(60, aspect, 0.01, 100);
    camera.position.set(0, 0.2, 1.2);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputEncoding = THREE.sRGBEncoding;
    containerRef.current.innerHTML = "";
    containerRef.current.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.rotateSpeed = 0.5;
    controlsRef.current = controls;

    scene.background = new THREE.Color("#eef2f3");

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
    dirLight.position.set(2, 2, 2);
    scene.add(ambientLight, dirLight);

    const loadStrands = async () => {
      try {
        const response = await fetch("http://localhost:8000/output/strands.json");
        const data = await response.json();

        const points = Array.isArray(data) ? data : data.points;
        if (!points || !Array.isArray(points)) {
          console.error("Arquivo strands.json inválido ou corrompido:", data);
          return;
        }

        const simulator = new HairSimulator({ points }, scene);
        simulatorRef.current = simulator;

        if (simulator.group) {
          const box = new THREE.Box3().setFromObject(simulator.group);
          const center = new THREE.Vector3();
          box.getCenter(center);
          controls.target.copy(center);
          controls.update();
          camera.lookAt(center);
        } else {
          console.warn("simulator.group está indefinido.");
        }
      } catch (error) {
        console.error("Erro ao carregar strands.json:", error);
      }
    };

    loadStrands();

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();


      if (simulatorRef.current && simulatorRef.current.physicsEnabled) {
        simulatorRef.current.update();
      }
      renderer.render(scene, camera);
    };

    animate();
  }, []);

  useEffect(() => {
    if (simulatorRef.current) {
      simulatorRef.current.setPhysicsEnabled(physicsOn);
    }
  }, [physicsOn, gravityStrength, windStrength, stiffness, damping]);


  const resetScene = async () => {
    const scene = sceneRef.current;
    const simulator = simulatorRef.current;
    const controls = controlsRef.current;
    const camera = cameraRef.current;

    if (!scene || !controls || !camera) return;

    // Remove simulador anterior
    if (simulator?.group) {
      scene.remove(simulator.group);
    }
    simulatorRef.current = null;

    // Recarrega os fios
    try {
      const response = await fetch("http://localhost:8000/output/strands.json");
      const data = await response.json();

      const points = Array.isArray(data) ? data : data.points;
      if (!points || !Array.isArray(points)) {
        console.error("Arquivo strands.json inválido ou corrompido:", data);
        return;
      }

      const newSimulator = new HairSimulator({ points }, scene);
      simulatorRef.current = newSimulator;

      if (newSimulator.group) {
        const box = new THREE.Box3().setFromObject(newSimulator.group);
        const center = new THREE.Vector3();
        box.getCenter(center);
        controls.target.copy(center);
        controls.update();
        camera.lookAt(center);
      }
    } catch (error) {
      console.error("Erro ao carregar strands.json:", error);
    }
  };



  return (
    <div className="app-container">
      <div className="sidebar">
        <h1>💇 Curly Hair Simulator</h1>
        <div className="card">

          <h3>🎞️ Animation Playground</h3>
          <div className="animation-cards">
            Select an animation type to see how the hair reacts:
            <br /><br />
            {["pendulum", "spiral", "noise", "breeze", "wave", "pulse", "chaos", "ripple", "zigzag", "flutter", "twist", "fountain"].map((type) => (
              <div
                key={type}
                className={`card-button ${animationType === type ? "selected" : ""}`}
                onClick={() => {
                  setAnimationType(type as AnimationType);
                  simulatorRef.current?.setAnimationType(type as AnimationType);
                }}
              >
                {type === "pendulum" && "🪫 Pendulum"}
                {type === "spiral" && "🌀 Spiral"}
                {type === "noise" && "🌫️ Noise"}
                {type === "breeze" && "🍃 Breeze"}
                {type === "wave" && "🌊 Wave"}
                {type === "pulse" && "💓 Pulse"}
                {type === "chaos" && "🔥 Chaos"}
                {type === "ripple" && "🌊 Ripple"}
                {type === "zigzag" && "⚡ Zigzag"}
                {type === "flutter" && "🦋 Flutter"}
                {type === "twist" && "🌀 Twist"}
                {type === "fountain" && "⛲ Fountain"}
              </div>
            ))}
          </div>




          <button
            onClick={resetScene}
            style={{ backgroundColor: "#2980b9", color: "white" }}
          >
            🔄 Reset Scene
          </button>

          <button
            onClick={() => setPhysicsOn(!physicsOn)}
            style={{ backgroundColor: physicsOn ? "#c0392b" : "#27ae60", marginBottom: "10px" }}
          >
            {physicsOn ? "🛑 Disable Physics" : "▶️ Enable Physics"}
          </button>

        </div>
      </div>
      <div className="preview" ref={containerRef}></div>
    </div>
  );
}