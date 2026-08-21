"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { motion } from "framer-motion";
import { Shield, Sparkles, Activity, Lock, Cpu } from "lucide-react";

export const CoreAperture: React.FC = () => {
  const { persona, aiState, audioWaveforms } = useJarvis();

  // Dynamic values based on AIState
  const isThinking = aiState === "THINKING";
  const isExecuting = aiState === "EXECUTING";
  const isListening = aiState === "LISTENING";

  const averageWave =
    audioWaveforms.reduce((acc, v) => acc + v, 0) / (audioWaveforms.length || 1);

  return (
    <div className="relative flex flex-col items-center justify-center p-6 glass-panel overflow-hidden w-full aspect-square max-w-[340px] mx-auto group">
      {/* Subtle Background Radial Aura */}
      <div className="absolute inset-0 bg-primary/5 rounded-full filter blur-3xl transition-opacity duration-700 opacity-60 group-hover:opacity-100" />

      {/* Persona Core Container */}
      <div className="relative w-64 h-64 flex items-center justify-center">
        {/* =========================================================================
            E.V. PERSONA: Bioluminescent Multi-Layer Rotating Reticle & Neural Wave
           ========================================================================= */}
        {persona === "ev" ? (
          <div className="relative w-full h-full flex items-center justify-center">
            {/* Outer Cybernetic Ring */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 24, ease: "linear" }}
              className="absolute inset-0 rounded-full border border-dashed border-primary/30"
            />

            {/* Middle Reverse Ring with Angled Calibrations */}
            <motion.div
              animate={{ rotate: -360 }}
              transition={{ repeat: Infinity, duration: 16, ease: "linear" }}
              className="absolute inset-3 rounded-full border-2 border-secondary/40 border-t-primary border-r-transparent glow-box"
            />

            {/* Neural Waveform SVG Canvas */}
            <svg className="absolute inset-6 w-52 h-52 pointer-events-none" viewBox="0 0 100 100">
              <defs>
                <linearGradient id="evGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--color-primary)" />
                  <stop offset="100%" stopColor="var(--color-secondary)" />
                </linearGradient>
              </defs>

              {/* Reactive Circular Waveform */}
              <motion.circle
                cx="50"
                cy="50"
                r={28 + averageWave * 12}
                fill="none"
                stroke="url(#evGradient)"
                strokeWidth="1.8"
                strokeDasharray="4 3"
                className="glow-box"
              />

              <motion.circle
                cx="50"
                cy="50"
                r={20 + averageWave * 6}
                fill="rgba(255, 42, 77, 0.08)"
                stroke="var(--color-primary)"
                strokeWidth="1.2"
              />
            </svg>

            {/* Central Bio-Node */}
            <motion.div
              animate={{
                scale: isListening ? [1, 1.25, 1] : isThinking ? [0.9, 1.1, 0.9] : [1, 1.05, 1],
                boxShadow: isExecuting ? "0 0 35px var(--color-primary)" : "0 0 18px var(--color-glow)",
              }}
              transition={{ repeat: Infinity, duration: isListening ? 0.8 : 2 }}
              className="relative z-10 w-16 h-16 rounded-full bg-primary/20 border-2 border-primary flex items-center justify-center text-primary backdrop-blur-md"
            >
              <Sparkles className={`w-8 h-8 ${isThinking ? "animate-spin" : "animate-pulse"}`} />
            </motion.div>
          </div>
        ) : (
          /* =========================================================================
             ALFRED PERSONA: Wayne-Tech Tactical Astrolabe & Mechanical Aperture
             ========================================================================= */
          <div className="relative w-full h-full flex items-center justify-center font-mono">
            {/* Outer Precision Astrolabe Ring (90° Orthogonal Grids) */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 30, ease: "linear" }}
              className="absolute inset-0 rounded-full border border-primary/40 flex items-center justify-center"
            >
              <div className="absolute top-0 w-1 h-3 bg-primary" />
              <div className="absolute bottom-0 w-1 h-3 bg-primary" />
              <div className="absolute left-0 h-1 w-3 bg-primary" />
              <div className="absolute right-0 h-1 w-3 bg-primary" />
            </motion.div>

            {/* Inner Mechanical Aperture / Iris Blades */}
            <motion.div
              animate={{
                rotate: isThinking ? -180 : isExecuting ? 90 : 0,
                scale: isThinking ? 0.82 : isExecuting ? 0.75 : 1,
              }}
              transition={{ duration: 0.8, ease: "easeInOut" }}
              className="absolute inset-5 rounded-full border border-secondary flex items-center justify-center"
            >
              {/* 6 Interlocking Iris Blades */}
              {[0, 60, 120, 180, 240, 300].map((deg) => (
                <motion.div
                  key={deg}
                  style={{ transform: `rotate(${deg}deg)` }}
                  animate={{
                    width: isThinking ? "42px" : isExecuting ? "50px" : "32px",
                  }}
                  className="absolute h-0.5 bg-primary/80 origin-left"
                />
              ))}
            </motion.div>

            {/* Tactical Crosshair / Lock Core */}
            <motion.div
              animate={{
                scale: isExecuting ? [1, 1.15, 1] : 1,
                borderColor: isExecuting ? "var(--color-primary)" : "var(--color-border)",
              }}
              transition={{ duration: 0.5 }}
              className="relative z-10 w-16 h-16 rounded-sm bg-black/70 border border-primary/50 flex flex-col items-center justify-center glow-box"
            >
              {isExecuting ? (
                <Lock className="w-6 h-6 text-primary animate-pulse" />
              ) : isThinking ? (
                <Cpu className="w-6 h-6 text-primary animate-spin" />
              ) : (
                <Shield className="w-6 h-6 text-primary" />
              )}
              <span className="text-[8px] font-bold text-foreground/80 mt-1 uppercase tracking-wider">
                {aiState}
              </span>
            </motion.div>
          </div>
        )}
      </div>

      {/* Status Bar Telemetry under Aperture */}
      <div className="w-full mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-[10px] font-mono text-foreground/70">
        <span className="flex items-center gap-1.5">
          <Activity className="w-3 h-3 text-primary animate-pulse" />
          <span>FREQUENCY: <strong>{(averageWave * 120).toFixed(1)} Hz</strong></span>
        </span>
        <span className="uppercase text-primary font-bold tracking-widest">
          {persona === "ev" ? "BIO_RESONANCE_OK" : "APERTURE_CALIBRATED"}
        </span>
      </div>
    </div>
  );
};
