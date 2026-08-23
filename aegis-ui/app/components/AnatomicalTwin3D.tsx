"use client";

import React, { useEffect, useRef } from "react";
import * as THREE from "three";

interface AnatomicalTwin3DProps {
  heartRate: number;
  temperature: number;
  eda: number;
  syncopeDetected: boolean;
  isAnomaly: boolean;
}

export default function AnatomicalTwin3D({
  heartRate,
  temperature,
  eda,
  syncopeDetected,
  isAnomaly,
}: AnatomicalTwin3DProps) {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 320;
    const height = container.clientHeight || 300;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 18);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    // 2. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x06b6d4, 1.5);
    dirLight.position.set(5, 10, 7);
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0xf43f5e, 2, 20);
    pointLight.position.set(0, 1.5, 3);
    scene.add(pointLight);

    // 3. Anatomical Silhouette Hologram Group
    const twinGroup = new THREE.Group();
    scene.add(twinGroup);

    // Wireframe Torso Skeleton Grid
    const torsoGeo = new THREE.CylinderGeometry(2.2, 1.6, 5.5, 16, 8, true);
    const torsoMat = new THREE.MeshBasicMaterial({
      color: 0x0ea5e9,
      wireframe: true,
      transparent: true,
      opacity: 0.25,
    });
    const torsoMesh = new THREE.Mesh(torsoGeo, torsoMat);
    torsoMesh.position.y = 0.5;
    twinGroup.add(torsoMesh);

    // Head
    const headGeo = new THREE.SphereGeometry(1.2, 16, 16);
    const headMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      wireframe: true,
      transparent: true,
      opacity: 0.3,
    });
    const headMesh = new THREE.Mesh(headGeo, headMat);
    headMesh.position.y = 4.2;
    twinGroup.add(headMesh);

    // 4. Beating 3D Heart Organ Mesh
    const heartShape = new THREE.Shape();
    heartShape.moveTo(0, 0);
    heartShape.bezierCurveTo(0, 0.5, -0.6, 1.2, -1.2, 1.2);
    heartShape.bezierCurveTo(-1.8, 1.2, -1.8, 0.4, -1.8, 0.4);
    heartShape.bezierCurveTo(-1.8, -0.4, -0.8, -1.2, 0, -1.8);
    heartShape.bezierCurveTo(0.8, -1.2, 1.8, -0.4, 1.8, 0.4);
    heartShape.bezierCurveTo(1.8, 0.4, 1.8, 1.2, 1.2, 1.2);
    heartShape.bezierCurveTo(0.6, 1.2, 0, 0.5, 0, 0);

    const extrudeSettings = { depth: 0.5, bevelEnabled: true, bevelSegments: 3, steps: 2, bevelSize: 0.2, bevelThickness: 0.2 };
    const heartGeo = new THREE.ExtrudeGeometry(heartShape, extrudeSettings);
    const heartMat = new THREE.MeshStandardMaterial({
      color: isAnomaly || syncopeDetected ? 0xf43f5e : 0x06b6d4,
      emissive: isAnomaly || syncopeDetected ? 0x9f1239 : 0x083344,
      roughness: 0.2,
      metalness: 0.8,
      wireframe: false,
    });
    const heartMesh = new THREE.Mesh(heartGeo, heartMat);
    heartMesh.scale.set(0.4, 0.4, 0.4);
    heartMesh.rotation.z = Math.PI;
    heartMesh.position.set(-0.3, 1.2, 0.6);
    twinGroup.add(heartMesh);

    // 5. Dual Lung Lobes Mesh
    const lungGeo = new THREE.CapsuleGeometry(0.7, 1.8, 8, 16);
    const lungMat = new THREE.MeshStandardMaterial({
      color: 0x10b981,
      transparent: true,
      opacity: 0.4,
      wireframe: true,
    });
    const leftLung = new THREE.Mesh(lungGeo, lungMat);
    leftLung.position.set(-1.1, 1.0, 0.2);
    leftLung.rotation.z = 0.15;
    twinGroup.add(leftLung);

    const rightLung = new THREE.Mesh(lungGeo, lungMat);
    rightLung.position.set(1.1, 1.0, 0.2);
    rightLung.rotation.z = -0.15;
    twinGroup.add(rightLung);

    // 6. Vascular Conduit Ring Orbitals
    const ringGeo = new THREE.RingGeometry(3.2, 3.25, 32);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x06b6d4, side: THREE.DoubleSide, transparent: true, opacity: 0.3 });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 2.5;
    twinGroup.add(ringMesh);

    // 7. Animation Loop with Dynamic BPM Heart Rate Throbbing
    let animationFrameId: number;
    let clock = new THREE.Clock();

    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;
        twinGroup.rotation.y += deltaX * 0.01;
        twinGroup.rotation.x += deltaY * 0.01;
        previousMousePosition = { x: e.clientX, y: e.clientY };
      }
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    container.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    const animate = () => {
      const elapsedTime = clock.getElapsedTime();

      // Dynamic Heart Beat pulse synced to heartRate
      const hrBps = heartRate / 60;
      const beatCycle = Math.sin(elapsedTime * hrBps * Math.PI * 2);
      const pulseScale = 0.4 + (beatCycle > 0.6 ? beatCycle * 0.08 : 0);
      heartMesh.scale.set(pulseScale, pulseScale, pulseScale);

      // Lung respiration expansion
      const lungCycle = Math.sin(elapsedTime * 1.5) * 0.06;
      leftLung.scale.set(1 + lungCycle, 1 + lungCycle, 1 + lungCycle);
      rightLung.scale.set(1 + lungCycle, 1 + lungCycle, 1 + lungCycle);

      // Auto gentle hover rotation
      if (!isDragging) {
        twinGroup.rotation.y += 0.008;
      }
      ringMesh.rotation.z += 0.01;

      // Dynamic color update on anomaly
      if (isAnomaly || syncopeDetected) {
        heartMat.color.setHex(0xf43f5e);
        heartMat.emissive.setHex(0x9f1239);
      } else {
        heartMat.color.setHex(0x06b6d4);
        heartMat.emissive.setHex(0x083344);
      }

      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
    };
  }, [heartRate, temperature, eda, syncopeDetected, isAnomaly]);

  return (
    <div className="relative w-full h-[260px] rounded-2xl bg-slate-950/90 border border-slate-800 overflow-hidden shadow-inner flex items-center justify-center cursor-grab active:cursor-grabbing">
      <div ref={mountRef} className="w-full h-full" />
      
      {/* 3D HUD Badges */}
      <div className="absolute top-2 left-2 px-2 py-1 rounded bg-black/70 backdrop-blur border border-cyan-500/40 text-[9px] font-mono text-cyan-300 flex items-center gap-1.5 pointer-events-none">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
        <span>3D DIGITAL TWIN // HR PULSE {heartRate} BPM</span>
      </div>

      <div className="absolute top-2 right-2 px-2 py-1 rounded bg-black/70 backdrop-blur border border-slate-700 text-[9px] font-mono text-slate-400 pointer-events-none">
        INTERACTIVE 360° WEBGL
      </div>

      <div className="absolute bottom-2 inset-x-2 flex justify-between text-[9px] font-mono pointer-events-none">
        <span className="px-2 py-0.5 rounded bg-slate-900/80 border border-slate-800 text-slate-300">
          Lungs: Respiration Nominal
        </span>
        <span className={`px-2 py-0.5 rounded border ${isAnomaly || syncopeDetected ? "bg-rose-950/80 border-rose-500 text-rose-300" : "bg-cyan-950/80 border-cyan-500 text-cyan-300"}`}>
          Cardiac: {heartRate > 100 ? "TACHYCARDIA ALERT" : "Vascular Flow 100%"}
        </span>
      </div>
    </div>
  );
}
