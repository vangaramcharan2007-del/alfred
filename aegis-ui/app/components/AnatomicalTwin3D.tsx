"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { Sparkles, Heart, Activity, AlertCircle, Info, ChevronRight, User } from "lucide-react";

interface AnatomicalTwin3DProps {
  gender: string;
  heartRate: number;
  temperature: number;
  eda: number;
  syncopeDetected: boolean;
  isAnomaly: boolean;
  selectedDisease?: string;
  onSelectOrgan?: (organName: string, diseaseInfo: any) => void;
}

interface DiseaseExplainer {
  title: string;
  organ: string;
  severity: "NORMAL" | "MODERATE" | "CRITICAL";
  whatIsIt: string;
  whatToDo: string;
  color: string;
}

const DISEASE_PRESETS: Record<string, DiseaseExplainer> = {
  NOMINAL: {
    title: "Physiological Equilibrium",
    organ: "Whole Body Perfusion",
    severity: "NORMAL",
    whatIsIt: "All organ subsystems are operating within resting homeostatic limits.",
    whatToDo: "Maintain hydration, balanced nutrition, and regular physical activity.",
    color: "#06b6d4"
  },
  CARDIAC_TACHYCARDIA: {
    title: "Cardiac Arrhythmia / Tachycardia",
    organ: "Heart & Vascular Chambers",
    severity: "CRITICAL",
    whatIsIt: "Heart rate is elevated (>100 BPM), causing increased myocardial oxygen demand and autonomic cardiac strain.",
    whatToDo: "Sit comfortably, avoid caffeine/stimulants, perform slow 4-7-8 breathing, and monitor pulse.",
    color: "#f43f5e"
  },
  BRONCHIAL_ASTHMA: {
    title: "Bronchial Airway Constriction",
    organ: "Lungs & Tracheobronchial Tree",
    severity: "MODERATE",
    whatIsIt: "Inflammation and smooth muscle spasm narrowing the bronchial airways, reducing airflow.",
    whatToDo: "Sit upright, loosen tight clothing, administer 2 puffs of Salbutamol inhaler as prescribed.",
    color: "#f59e0b"
  },
  ACUTE_FEVER: {
    title: "Acute Hyperthermia & Pyrexia",
    organ: "Hypothalamus & Core Thermoregulation",
    severity: "CRITICAL",
    whatIsIt: "Core temperature spiked above 38.5°C in response to pyrogens, causing systemic metabolic acceleration.",
    whatToDo: "Apply cool compress to forehead/neck, drink oral rehydration fluids, take Paracetamol (avoid Ibuprofen if allergic).",
    color: "#ec4899"
  },
  ANEMIA_PALLOR: {
    title: "Microvascular Anemia & Hypoperfusion",
    organ: "Capillary Perfusion & Blood Oxygenation",
    severity: "MODERATE",
    whatIsIt: "Reduced hemoglobin concentration lowering oxygen delivery to peripheral tissues and brain.",
    whatToDo: "Take oral Ferrous Sulfate with vitamin C/citrus. Increase leafy greens and iron-rich lentils.",
    color: "#a855f7"
  },
  SYNCOPE_COLLAPSE: {
    title: "Postural Syncope / Transient Ischemia",
    organ: "Cerebral Hypoperfusion & Vasomotor Core",
    severity: "CRITICAL",
    whatIsIt: "Sudden drop in systemic blood pressure and cerebral blood flow resulting in fainting/collapse.",
    whatToDo: "Lay flat on back immediately and elevate legs 30 cm. Do NOT stand up quickly.",
    color: "#e11d48"
  },
  DYSMENORRHEA: {
    title: "Acute Dysmenorrhea / Pelvic Cramping",
    organ: "Pelvic Smooth Muscle & Uterine Myometrium",
    severity: "MODERATE",
    whatIsIt: "Prostaglandin-induced uterine contractions causing localized lower abdominal discomfort and spasms.",
    whatToDo: "Apply warm heating pad to lower abdomen, practice gentle lumbar stretching, take prescribed antispasmodic.",
    color: "#d946ef"
  }
};

export default function AnatomicalTwin3D({
  gender = "Male",
  heartRate = 72,
  temperature = 36.8,
  eda = 1.5,
  syncopeDetected = false,
  isAnomaly = false,
  selectedDisease,
  onSelectOrgan,
}: AnatomicalTwin3DProps) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [activeDiseaseKey, setActiveDiseaseKey] = useState<string>("NOMINAL");
  const [activeOrgan, setActiveOrgan] = useState<string>("Heart");

  const isFemale = gender.toLowerCase() === "female";

  // Auto-detect active disease preset from vitals
  useEffect(() => {
    if (syncopeDetected) {
      setActiveDiseaseKey("SYNCOPE_COLLAPSE");
    } else if (temperature > 38.0) {
      setActiveDiseaseKey("ACUTE_FEVER");
    } else if (heartRate > 100) {
      setActiveDiseaseKey("CARDIAC_TACHYCARDIA");
    } else if (isFemale && selectedDisease === "DYSMENORRHEA") {
      setActiveDiseaseKey("DYSMENORRHEA");
    } else if (selectedDisease && DISEASE_PRESETS[selectedDisease]) {
      setActiveDiseaseKey(selectedDisease);
    } else {
      setActiveDiseaseKey("NOMINAL");
    }
  }, [syncopeDetected, temperature, heartRate, selectedDisease, isFemale]);

  const diseaseData = DISEASE_PRESETS[activeDiseaseKey] || DISEASE_PRESETS.NOMINAL;

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 360;
    const height = container.clientHeight || 360;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(0, 0.5, 17);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    // 2. Anatomical Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0x38bdf8, 2.0);
    mainLight.position.set(4, 8, 10);
    scene.add(mainLight);

    const organAccentLight = new THREE.PointLight(0xf43f5e, 2.5, 15);
    organAccentLight.position.set(0, 1.2, 2.5);
    scene.add(organAccentLight);

    // 3. Human Anatomical Model Group
    const twinGroup = new THREE.Group();
    scene.add(twinGroup);

    // Morphological Gender Proportions
    const shoulderW = isFemale ? 1.8 : 2.4;
    const waistW = isFemale ? 1.2 : 1.6;
    const hipW = isFemale ? 1.9 : 1.7;

    // Outer Anatomical Glass Silhouette Mesh
    const torsoGeo = new THREE.CylinderGeometry(shoulderW, hipW, 6.2, 24, 12, false);
    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0x0ea5e9,
      transmission: 0.85,
      opacity: 0.35,
      transparent: true,
      roughness: 0.15,
      ior: 1.35,
      wireframe: false,
    });
    const torsoMesh = new THREE.Mesh(torsoGeo, glassMat);
    torsoMesh.position.y = 0.6;
    twinGroup.add(torsoMesh);

    // Wireframe Outer Guide Cage
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      wireframe: true,
      transparent: true,
      opacity: 0.2,
    });
    const wireMesh = new THREE.Mesh(torsoGeo, wireMat);
    wireMesh.position.y = 0.6;
    wireMesh.scale.set(1.02, 1.02, 1.02);
    twinGroup.add(wireMesh);

    // Cranium / Brain Sphere
    const headGeo = new THREE.SphereGeometry(1.15, 24, 24);
    const headMat = new THREE.MeshStandardMaterial({
      color: activeDiseaseKey === "ACUTE_FEVER" || activeDiseaseKey === "SYNCOPE_COLLAPSE" ? 0xec4899 : 0x0284c7,
      emissive: activeDiseaseKey === "ACUTE_FEVER" ? 0xbe185d : 0x0369a1,
      roughness: 0.3,
      metalness: 0.4,
      transparent: true,
      opacity: 0.85,
    });
    const headMesh = new THREE.Mesh(headGeo, headMat);
    headMesh.position.y = 4.6;
    twinGroup.add(headMesh);

    // Cranial Halo Wave (fever / syncope indicator)
    const haloGeo = new THREE.TorusGeometry(1.4, 0.04, 16, 64);
    const haloMat = new THREE.MeshBasicMaterial({
      color: activeDiseaseKey === "ACUTE_FEVER" ? 0xf43f5e : 0x38bdf8,
      transparent: true,
      opacity: 0.6,
    });
    const haloMesh = new THREE.Mesh(haloGeo, haloMat);
    haloMesh.rotation.x = Math.PI / 2;
    haloMesh.position.y = 4.6;
    twinGroup.add(haloMesh);

    // 4. Detailed Anatomical Heart (Left Atrium, Ventricle, Aorta)
    const heartGroup = new THREE.Group();
    heartGroup.position.set(-0.35, 1.6, 0.6);

    const heartMainGeo = new THREE.SphereGeometry(0.7, 24, 24);
    heartMainGeo.scale(0.85, 1.1, 0.85);
    const heartColor = activeDiseaseKey === "CARDIAC_TACHYCARDIA" || isAnomaly ? 0xf43f5e : 0x0284c7;
    const heartMat = new THREE.MeshStandardMaterial({
      color: heartColor,
      emissive: isAnomaly || heartRate > 100 ? 0x9f1239 : 0x075985,
      roughness: 0.2,
      metalness: 0.7,
    });
    const heartMain = new THREE.Mesh(heartMainGeo, heartMat);
    heartGroup.add(heartMain);

    // Aortic Arch Tube
    const aortaCurve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, 0.4, 0),
      new THREE.Vector3(0.1, 0.9, 0.1),
      new THREE.Vector3(0.3, 1.1, -0.1),
      new THREE.Vector3(0.4, 0.7, -0.3),
    ]);
    const aortaGeo = new THREE.TubeGeometry(aortaCurve, 20, 0.14, 8, false);
    const aortaMat = new THREE.MeshStandardMaterial({ color: 0xe11d48, roughness: 0.3 });
    const aortaMesh = new THREE.Mesh(aortaGeo, aortaMat);
    heartGroup.add(aortaMesh);

    twinGroup.add(heartGroup);

    // 5. Dual Pulmonary Lung Lobes with Bronchial Tint
    const lungGeo = new THREE.CapsuleGeometry(0.75, 1.9, 12, 24);
    const lungMat = new THREE.MeshPhysicalMaterial({
      color: activeDiseaseKey === "BRONCHIAL_ASTHMA" ? 0xf59e0b : 0x10b981,
      emissive: activeDiseaseKey === "BRONCHIAL_ASTHMA" ? 0x78350f : 0x064e3b,
      transparent: true,
      opacity: 0.75,
      roughness: 0.3,
    });
    const leftLung = new THREE.Mesh(lungGeo, lungMat);
    leftLung.position.set(-1.15, 1.4, 0.1);
    leftLung.rotation.z = 0.12;
    twinGroup.add(leftLung);

    const rightLung = new THREE.Mesh(lungGeo, lungMat);
    rightLung.position.set(1.15, 1.4, 0.1);
    rightLung.rotation.z = -0.12;
    twinGroup.add(rightLung);

    // 6. Abdominal / Pelvic Organ Zone (Digestive & Dysmenorrhea)
    const pelvicGeo = new THREE.CylinderGeometry(0.8, 1.1, 1.2, 16);
    const pelvicColor = activeDiseaseKey === "DYSMENORRHEA" ? 0xd946ef : 0x059669;
    const pelvicMat = new THREE.MeshStandardMaterial({
      color: pelvicColor,
      emissive: activeDiseaseKey === "DYSMENORRHEA" ? 0x86198f : 0x022c22,
      transparent: true,
      opacity: 0.65,
      roughness: 0.3,
    });
    const pelvicMesh = new THREE.Mesh(pelvicGeo, pelvicMat);
    pelvicMesh.position.set(0, -1.2, 0.2);
    twinGroup.add(pelvicMesh);

    // 7. Interactive Raycasting for Clicking Organs
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const interactiveObjects = [
      { mesh: headMesh, name: "Brain / Head", disease: "ACUTE_FEVER" },
      { mesh: heartMain, name: "Cardiovascular Heart", disease: "CARDIAC_TACHYCARDIA" },
      { mesh: leftLung, name: "Left Pulmonary Lung", disease: "BRONCHIAL_ASTHMA" },
      { mesh: rightLung, name: "Right Pulmonary Lung", disease: "BRONCHIAL_ASTHMA" },
      { mesh: pelvicMesh, name: isFemale ? "Pelvic / Uterine Region" : "Digestive / Core Abdomen", disease: isFemale ? "DYSMENORRHEA" : "ANEMIA_PALLOR" }
    ];

    const onClick = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(interactiveObjects.map(o => o.mesh));

      if (intersects.length > 0) {
        const hit = interactiveObjects.find(o => o.mesh === intersects[0].object);
        if (hit) {
          setActiveOrgan(hit.name);
          setActiveDiseaseKey(hit.disease);
          if (onSelectOrgan) {
            onSelectOrgan(hit.name, DISEASE_PRESETS[hit.disease]);
          }
        }
      }
    };

    container.addEventListener("click", onClick);

    // 8. 360 Drag Controls
    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouse = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const dx = e.clientX - prevMouse.x;
        const dy = e.clientY - prevMouse.y;
        twinGroup.rotation.y += dx * 0.01;
        twinGroup.rotation.x += dy * 0.01;
        prevMouse = { x: e.clientX, y: e.clientY };
      }
    };

    const onMouseUp = () => { isDragging = false; };

    container.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    // 9. Animation Loop with Real-Time BPM Heart Throbbing & Lung Tidal Breathing
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      const elapsed = clock.getElapsedTime();

      // Dynamic Heart Beat pulse
      const bps = Math.max(40, Math.min(180, heartRate)) / 60;
      const heartBeat = Math.sin(elapsed * bps * Math.PI * 2);
      const hScale = 0.95 + (heartBeat > 0.5 ? (heartBeat - 0.5) * 0.25 : 0);
      heartGroup.scale.set(hScale, hScale, hScale);

      // Lung respiration
      const breath = Math.sin(elapsed * 1.6) * 0.06;
      leftLung.scale.set(1 + breath, 1 + breath, 1 + breath);
      rightLung.scale.set(1 + breath, 1 + breath, 1 + breath);

      // Cranial halo wave
      haloMesh.scale.set(1 + Math.sin(elapsed * 2) * 0.08, 1 + Math.sin(elapsed * 2) * 0.08, 1);

      if (!isDragging) {
        twinGroup.rotation.y += 0.006;
      }

      renderer.render(scene, camera);
      animId = requestAnimationFrame(animate);
    };

    animate();

    const onResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(animId);
      container.removeEventListener("click", onClick);
      container.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("resize", onResize);
      renderer.dispose();
    };
  }, [gender, heartRate, temperature, eda, syncopeDetected, isAnomaly, activeDiseaseKey]);

  return (
    <div className="flex flex-col gap-3 w-full">
      
      {/* Interactive 3D WebGL Canvas Viewport */}
      <div className="relative w-full h-[280px] rounded-3xl bg-[#090b14] border border-slate-800/80 overflow-hidden shadow-2xl flex items-center justify-center cursor-grab active:cursor-grabbing">
        <div ref={mountRef} className="w-full h-full" />
        
        {/* Top Badges */}
        <div className="absolute top-3 left-3 flex items-center gap-2 pointer-events-none">
          <div className="px-2.5 py-1 rounded-xl bg-black/80 backdrop-blur-md border border-cyan-500/40 text-[10px] font-mono text-cyan-300 flex items-center gap-1.5 shadow">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>3D TWIN: {gender.toUpperCase()} MORPHOLOGY</span>
          </div>
          <div className="px-2 py-1 rounded-xl bg-black/80 backdrop-blur-md border border-slate-700 text-[10px] font-mono text-slate-300">
            HR: <strong className="text-white">{heartRate} BPM</strong>
          </div>
        </div>

        <div className="absolute top-3 right-3 px-2 py-1 rounded-xl bg-black/80 backdrop-blur-md border border-slate-700 text-[9px] font-mono text-slate-400 pointer-events-none">
          TAP ORGAN TO INSPECT
        </div>

        {/* Bottom Status Ticker */}
        <div className="absolute bottom-3 inset-x-3 flex items-center justify-between pointer-events-none">
          <div className="px-2.5 py-1 rounded-xl bg-black/80 backdrop-blur-md border border-slate-800 text-[10px] font-mono text-slate-300">
            Target Focus: <strong className="text-cyan-400">{activeOrgan}</strong>
          </div>
          <div className={`px-2.5 py-1 rounded-xl backdrop-blur-md border text-[10px] font-mono font-bold ${
            diseaseData.severity === "CRITICAL"
              ? "bg-rose-950/90 border-rose-500 text-rose-300 animate-pulse"
              : diseaseData.severity === "MODERATE"
              ? "bg-amber-950/90 border-amber-500 text-amber-300"
              : "bg-emerald-950/90 border-emerald-500 text-emerald-300"
          }`}>
            {diseaseData.title}
          </div>
        </div>
      </div>

      {/* Disease Demonstration & Patient Guidance Card */}
      <div className="p-3.5 rounded-2xl bg-slate-900/90 border border-slate-800/90 flex flex-col gap-2 shadow-lg">
        
        {/* Quick Disease Filter Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 pb-1 border-b border-slate-800/80">
          <span className="text-[10px] font-mono text-slate-400 mr-1">SIMULATE CONDITIONS:</span>
          {Object.entries(DISEASE_PRESETS)
            .filter(([key]) => key !== "DYSMENORRHEA" || isFemale)
            .map(([key, item]) => {
              const isSelected = key === activeDiseaseKey;
              return (
                <button
                  key={key}
                  onClick={() => {
                    setActiveDiseaseKey(key);
                    setActiveOrgan(item.organ);
                  }}
                  className={`px-2 py-0.5 rounded-lg text-[10px] font-mono transition border ${
                    isSelected
                      ? "bg-cyan-500 text-slate-950 font-bold border-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.4)]"
                      : "bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
                  }`}
                >
                  {item.title.split("/")[0].trim()}
                </button>
              );
            })}
        </div>

        {/* Plain-Language Explainer for Patients */}
        <div className="space-y-1.5 text-xs font-mono">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: diseaseData.color }} />
            <h4 className="font-bold text-white text-xs tracking-wide">
              {diseaseData.title} <span className="text-slate-400 font-normal">({diseaseData.organ})</span>
            </h4>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 text-slate-300 space-y-1">
            <div className="text-[11px] text-slate-300 leading-relaxed">
              <strong className="text-cyan-300">What is happening:</strong> {diseaseData.whatIsIt}
            </div>
            <div className="text-[11px] text-emerald-300 leading-relaxed pt-0.5 border-t border-slate-800/60">
              <strong className="text-emerald-400">What you should do:</strong> {diseaseData.whatToDo}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
