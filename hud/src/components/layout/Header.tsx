"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Cpu, Shield, Globe, Radio, Sparkles, Activity, Layers } from "lucide-react";
import { motion } from "framer-motion";

export const Header: React.FC = () => {
  const {
    persona,
    togglePersona,
    aiState,
    audioWaveforms,
    meshNodes,
    totalVectors,
    worldMonitorActive,
    toggleWorldMonitor,
  } = useJarvis();

  const activeNodesCount = meshNodes.filter((n) => n.status === "online").length;

  return (
    <header className="w-full glass-panel px-6 py-3 border-b border-primary/20 flex flex-wrap items-center justify-between gap-4 relative z-30 font-mono text-xs">
      {/* Brand & Persona Identity */}
      <div className="flex items-center space-x-4">
        <div className="relative flex items-center justify-center">
          <div className="w-9 h-9 rounded-md border border-primary/40 flex items-center justify-center bg-primary/10 glow-box">
            {persona === "ev" ? (
              <Sparkles className="w-5 h-5 text-primary animate-pulse" />
            ) : (
              <Shield className="w-5 h-5 text-primary" />
            )}
          </div>
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-green-500 rounded-full animate-ping" />
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-green-500 rounded-full" />
        </div>

        <div>
          <div className="flex items-center space-x-2">
            <span className="font-black text-sm tracking-wider text-foreground glow-text">
              JARVIS X
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-primary/20 text-primary font-bold border border-primary/30 uppercase tracking-widest">
              {persona === "ev" ? "E.V. NEURAL CORE" : "ALFRED TACTICAL"}
            </span>
          </div>
          <p className="text-[10px] text-foreground/60 tracking-wider">
            SOVEREIGN COMPANION OF CHARAN &bull; MASTER MESH
          </p>
        </div>
      </div>

      {/* Simulated Waveform Visualizer & State Badge */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded bg-black/40 border border-white/10">
          <Radio className="w-3.5 h-3.5 text-primary animate-pulse" />
          <span className="text-[10px] font-bold text-foreground/80 uppercase">
            STATE: <span className="text-primary font-black glow-text">{aiState}</span>
          </span>

          {/* 16-Bar Audio Waveform */}
          <div className="flex items-center space-x-0.5 h-4 w-28 px-1">
            {audioWaveforms.slice(0, 16).map((val, idx) => (
              <motion.div
                key={idx}
                animate={{ height: `${Math.max(15, val * 100)}%` }}
                transition={{ duration: 0.05 }}
                className="w-1 bg-primary rounded-t glow-box"
              />
            ))}
          </div>
        </div>

        {/* Telemetry Pills */}
        <div className="hidden lg:flex items-center space-x-3 text-[11px] text-foreground/70">
          <div className="flex items-center space-x-1.5">
            <Cpu className="w-3.5 h-3.5 text-primary" />
            <span>NODES: <strong className="text-foreground">{activeNodesCount}/5 ACTIVE</strong></span>
          </div>
          <div className="flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-primary" />
            <span>BRAIN: <strong className="text-foreground">{totalVectors.toLocaleString()} VECTORS</strong></span>
          </div>
          <div className="flex items-center space-x-1.5">
            <Activity className="w-3.5 h-3.5 text-green-400 animate-pulse" />
            <span>LATENCY: <strong className="text-green-400">12ms</strong></span>
          </div>
        </div>
      </div>

      {/* Action Controls: World Monitor & Persona Switcher */}
      <div className="flex items-center space-x-2">
        <button
          onClick={toggleWorldMonitor}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded transition-all uppercase tracking-wider font-bold border ${
            worldMonitorActive
              ? "bg-primary text-black border-primary shadow-[0_0_15px_var(--color-primary)]"
              : "bg-surface text-foreground/80 border-white/10 hover:border-primary/40 hover:text-primary"
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          <span>WORLD MONITOR</span>
        </button>

        <button
          onClick={togglePersona}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-primary/15 hover:bg-primary/25 text-primary border border-primary/40 transition-all uppercase tracking-wider font-bold glow-box"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>SWAP PERSONA ({persona === "ev" ? "ALFRED" : "E.V."})</span>
        </button>
      </div>
    </header>
  );
};
