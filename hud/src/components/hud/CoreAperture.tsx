"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { motion } from "framer-motion";
import { Shield, Sparkles, Lock, Cpu, Radio, Target } from "lucide-react";

export const CoreAperture: React.FC = () => {
  const { persona, aiState, audioWaveforms } = useJarvis();

  const isThinking = aiState === "THINKING";
  const isExecuting = aiState === "EXECUTING";
  const isListening = aiState === "LISTENING";

  const avgWave = audioWaveforms.reduce((a, b) => a + b, 0) / (audioWaveforms.length || 1);

  // Aperture blade count for Mechanical Iris
  const bladeCount = 8;
  const blades = Array.from({ length: bladeCount }, (_, i) => i * (360 / bladeCount));

  // Generate 72 tactical tick marks for outer ring (every 5 degrees)
  const ticks = Array.from({ length: 72 }, (_, i) => i * 5);

  return (
    <div className="relative flex flex-col items-center justify-center p-6 spatial-glass hud-bracket overflow-hidden w-full aspect-square max-w-[480px] mx-auto group">
      {/* Background Radial Glow & Ambient Flares */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/10 via-transparent to-transparent pointer-events-none" />
      <div className="absolute w-72 h-72 rounded-full bg-primary/15 filter blur-[90px] pointer-events-none transition-all duration-700 group-hover:scale-110" />

      {/* Top HUD Telemetry Tags */}
      <div className="w-full flex items-center justify-between text-[9px] text-foreground/50 tracking-widest uppercase mb-1 z-10">
        <span className="flex items-center gap-1">
          <Target className="w-3 h-3 text-primary animate-pulse" />
          <span>GRID: <strong>WAYNE_SEC_09</strong></span>
        </span>
        <span className="text-primary font-bold glow-primary">
          {persona === "ev" ? "NEURAL_SYNAPSE_CORE" : "MECHANICAL_IRIS_v4.2"}
        </span>
        <span>LATENCY: <strong>{(avgWave * 18).toFixed(1)}ms</strong></span>
      </div>

      {/* =========================================================================
          CENTRAL MASSIVE SVG CANVAS (440x440 VIEWPORT)
         ========================================================================= */}
      <div className="relative w-[380px] h-[380px] sm:w-[420px] sm:h-[420px] flex items-center justify-center">
        {persona === "ev" ? (
          /* =========================================================================
             E.V. PERSONA: Cybernetic Neural Lab & Bioluminescent Waveform SVG
             ========================================================================= */
          <div className="relative w-full h-full flex items-center justify-center">
            {/* SVG Layer 1: Outer Holographic Gyroscope */}
            <motion.svg
              className="absolute inset-0 w-full h-full pointer-events-none"
              viewBox="0 0 400 400"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 40, ease: "linear" }}
            >
              <defs>
                <linearGradient id="evGradOuter" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FF2A4D" stopOpacity="0.8" />
                  <stop offset="50%" stopColor="#8A2BE2" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#FF2A4D" stopOpacity="0.8" />
                </linearGradient>
              </defs>

              {/* 360-Degree Radial Calibrations */}
              {ticks.map((deg) => {
                const isMajor = deg % 45 === 0;
                const r1 = 188;
                const r2 = isMajor ? 174 : 182;
                const rad = (deg * Math.PI) / 180;
                const x1 = 200 + r1 * Math.cos(rad);
                const y1 = 200 + r1 * Math.sin(rad);
                const x2 = 200 + r2 * Math.cos(rad);
                const y2 = 200 + r2 * Math.sin(rad);
                return (
                  <line
                    key={deg}
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke="url(#evGradOuter)"
                    strokeWidth={isMajor ? "2" : "0.8"}
                    strokeOpacity={isMajor ? "0.9" : "0.4"}
                  />
                );
              })}

              <circle cx="200" cy="200" r="190" fill="none" stroke="rgba(255,42,77,0.3)" strokeWidth="1" strokeDasharray="12 6" />
              <circle cx="200" cy="200" r="165" fill="none" stroke="rgba(138,43,226,0.35)" strokeWidth="1.5" strokeDasharray="4 8" />
            </motion.svg>

            {/* SVG Layer 2: Counter-Rotating Neural Synapse Nodes */}
            <motion.svg
              className="absolute inset-4 w-[92%] h-[92%] pointer-events-none"
              viewBox="0 0 400 400"
              animate={{ rotate: -360 }}
              transition={{ repeat: Infinity, duration: 25, ease: "linear" }}
            >
              {/* Interlocking Hexagonal Topology */}
              <polygon
                points="200,60 321,130 321,270 200,340 79,270 79,130"
                fill="none"
                stroke="rgba(255,42,77,0.4)"
                strokeWidth="1.2"
                strokeDasharray="8 6"
              />
              <polygon
                points="200,90 295,145 295,255 200,310 105,255 105,145"
                fill="none"
                stroke="rgba(138,43,226,0.5)"
                strokeWidth="1"
              />
              {/* Synapse Connection Nodes */}
              {[60, 130, 270, 340].map((coord, i) => (
                <circle key={i} cx="200" cy={coord} r="3" fill="#FF2A4D" className="animate-ping" />
              ))}
            </motion.svg>

            {/* SVG Layer 3: Dense Multi-Harmonic Neural Waveforms */}
            <svg className="absolute inset-10 w-[80%] h-[80%] pointer-events-none" viewBox="0 0 300 300">
              <defs>
                <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#FF2A4D" />
                  <stop offset="50%" stopColor="#C084FC" />
                  <stop offset="100%" stopColor="#8A2BE2" />
                </linearGradient>
              </defs>

              {/* Reactive Waveform 1 (Sine Harmonic A) */}
              <motion.path
                d={`M 30 150 Q 75 ${150 - avgWave * 90} 150 150 T 270 150`}
                fill="none"
                stroke="url(#waveGrad)"
                strokeWidth="3.5"
                className="glow-svg"
              />

              {/* Reactive Waveform 2 (Sine Harmonic B) */}
              <motion.path
                d={`M 30 150 Q 75 ${150 + avgWave * 75} 150 150 T 270 150`}
                fill="none"
                stroke="rgba(138, 43, 226, 0.75)"
                strokeWidth="2.2"
                strokeDasharray="5 3"
              />

              {/* Reactive Circular Bio-Resonance Ring */}
              <motion.circle
                cx="150"
                cy="150"
                r={45 + avgWave * 30}
                fill="none"
                stroke="rgba(255, 42, 77, 0.6)"
                strokeWidth="2"
                strokeDasharray="8 4"
                className="glow-svg"
              />
            </svg>

            {/* Central Bio-Singularity Core */}
            <motion.div
              animate={{
                scale: isListening ? [1, 1.35, 1] : isThinking ? [0.85, 1.15, 0.85] : isExecuting ? [1.1, 1.25, 1.1] : [1, 1.06, 1],
                boxShadow: isExecuting
                  ? "0 0 50px #FF2A4D, inset 0 0 20px #8A2BE2"
                  : "0 0 25px rgba(255,42,77,0.6)",
              }}
              transition={{ repeat: Infinity, duration: isListening ? 0.7 : 2 }}
              className="relative z-20 w-24 h-24 rounded-full bg-black/80 border-2 border-primary flex flex-col items-center justify-center backdrop-blur-2xl"
            >
              <Sparkles className={`w-9 h-9 text-primary ${isThinking ? "animate-spin" : "animate-pulse"}`} />
              <span className="text-[8px] font-black text-primary tracking-widest uppercase mt-1">
                {aiState}
              </span>
            </motion.div>
          </div>
        ) : (
          /* =========================================================================
             ALFRED PERSONA: Wayne-Tech Astrolabe & Real Mechanical Iris Aperture
             ========================================================================= */
          <div className="relative w-full h-full flex items-center justify-center">
            {/* SVG Layer 1: Outer Precision Astrolabe with Degrees & Degree Labels */}
            <motion.svg
              className="absolute inset-0 w-full h-full pointer-events-none"
              viewBox="0 0 400 400"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 60, ease: "linear" }}
            >
              <defs>
                <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#D4AF37" />
                  <stop offset="50%" stopColor="#F59E0B" />
                  <stop offset="100%" stopColor="#D4AF37" />
                </linearGradient>
              </defs>

              {/* 360-Degree Radial Precision Tick Marks */}
              {ticks.map((deg) => {
                const isCardinal = deg % 90 === 0;
                const isMajor = deg % 30 === 0;
                const r1 = 192;
                const r2 = isCardinal ? 172 : isMajor ? 178 : 184;
                const rad = (deg * Math.PI) / 180;
                const x1 = 200 + r1 * Math.cos(rad);
                const y1 = 200 + r1 * Math.sin(rad);
                const x2 = 200 + r2 * Math.cos(rad);
                const y2 = 200 + r2 * Math.sin(rad);
                return (
                  <line
                    key={deg}
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke="url(#goldGrad)"
                    strokeWidth={isCardinal ? "2.5" : isMajor ? "1.5" : "0.75"}
                    strokeOpacity={isCardinal ? "1" : isMajor ? "0.8" : "0.35"}
                  />
                );
              })}

              {/* Cardinal Labels */}
              <text x="200" y="28" fill="#D4AF37" fontSize="8" fontWeight="bold" textAnchor="middle" fontFamily="monospace">000° NORTH</text>
              <text x="375" y="203" fill="#D4AF37" fontSize="8" fontWeight="bold" textAnchor="middle" fontFamily="monospace">090° EAST</text>
              <text x="200" y="380" fill="#D4AF37" fontSize="8" fontWeight="bold" textAnchor="middle" fontFamily="monospace">180° SOUTH</text>
              <text x="25" y="203" fill="#D4AF37" fontSize="8" fontWeight="bold" textAnchor="middle" fontFamily="monospace">270° WEST</text>

              {/* Outer Nested Rings */}
              <circle cx="200" cy="200" r="194" fill="none" stroke="rgba(212,175,55,0.4)" strokeWidth="1.2" />
              <circle cx="200" cy="200" r="168" fill="none" stroke="rgba(212,175,55,0.3)" strokeWidth="1" strokeDasharray="16 8" />
              <circle cx="200" cy="200" r="148" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.8" strokeDasharray="4 6" />
            </motion.svg>

            {/* SVG Layer 2: Counter-Rotating Precision Gear Ring */}
            <motion.svg
              className="absolute inset-8 w-[84%] h-[84%] pointer-events-none"
              viewBox="0 0 300 300"
              animate={{ rotate: -360 }}
              transition={{ repeat: Infinity, duration: 35, ease: "linear" }}
            >
              {/* Tactical Bracket Crossbars */}
              <line x1="20" y1="150" x2="280" y2="150" stroke="rgba(212,175,55,0.25)" strokeWidth="1" strokeDasharray="6 4" />
              <line x1="150" y1="20" x2="150" y2="280" stroke="rgba(212,175,55,0.25)" strokeWidth="1" strokeDasharray="6 4" />
              <circle cx="150" cy="150" r="120" fill="none" stroke="#D4AF37" strokeWidth="1.5" strokeDasharray="24 12" />
            </motion.svg>

            {/* SVG Layer 3: REAL OVERLAPPING MECHANICAL IRIS APERTURE BLADES */}
            <div className="relative w-56 h-56 flex items-center justify-center">
              <motion.div
                animate={{
                  rotate: isThinking ? -180 : isExecuting ? 120 : 0,
                  scale: isThinking ? 0.78 : isExecuting ? 0.7 : 1,
                }}
                transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                className="relative w-full h-full flex items-center justify-center"
              >
                <svg className="w-full h-full" viewBox="0 0 200 200">
                  <defs>
                    <linearGradient id="bladeMetal" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#2A2F3A" />
                      <stop offset="50%" stopColor="#1E222A" />
                      <stop offset="100%" stopColor="#0E1117" />
                    </linearGradient>
                  </defs>

                  {/* 8 Interlocking Overlapping Precision Curved Blades */}
                  {blades.map((deg, i) => (
                    <g key={i} transform={`rotate(${deg} 100 100)`}>
                      <path
                        d="M 100,20 C 135,20 165,50 165,85 L 140,115 C 120,95 105,80 85,85 Z"
                        fill="url(#bladeMetal)"
                        stroke="#D4AF37"
                        strokeWidth="1.2"
                        strokeOpacity="0.85"
                        className="transition-all duration-700"
                      />
                      {/* Blade Precision Bevel Line */}
                      <line x1="100" y1="20" x2="140" y2="115" stroke="rgba(212,175,55,0.4)" strokeWidth="0.8" />
                    </g>
                  ))}

                  {/* Center Aperture Iris Ring */}
                  <circle
                    cx="100"
                    cy="100"
                    r={isThinking ? "22" : isExecuting ? "16" : "32"}
                    fill="none"
                    stroke="#D4AF37"
                    strokeWidth="2"
                    className="glow-svg transition-all duration-700"
                  />
                </svg>
              </motion.div>

              {/* Central Optical Singularity / Lock Core */}
              <motion.div
                animate={{
                  scale: isExecuting ? [1, 1.18, 1] : 1,
                  borderColor: isExecuting ? "#D4AF37" : "rgba(212,175,55,0.4)",
                  boxShadow: isExecuting
                    ? "0 0 45px #D4AF37, inset 0 0 15px #D4AF37"
                    : "0 0 20px rgba(212,175,55,0.3)",
                }}
                transition={{ repeat: isExecuting ? Infinity : 0, duration: 1.2 }}
                className="absolute z-20 w-20 h-20 rounded-md bg-black/90 border border-primary/60 flex flex-col items-center justify-center backdrop-blur-2xl"
              >
                {isExecuting ? (
                  <Lock className="w-7 h-7 text-primary animate-pulse" />
                ) : isThinking ? (
                  <Cpu className="w-7 h-7 text-primary animate-spin" />
                ) : isListening ? (
                  <Radio className="w-7 h-7 text-primary animate-pulse" />
                ) : (
                  <Shield className="w-7 h-7 text-primary" />
                )}
                <span className="text-[8px] font-black text-primary tracking-widest uppercase mt-1">
                  {aiState}
                </span>
              </motion.div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Telemetry Bar */}
      <div className="w-full mt-2 pt-2.5 border-t border-white/10 flex items-center justify-between text-[9px] text-foreground/60 tracking-wider">
        <span className="flex items-center gap-1.5 text-primary font-bold">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
          <span>RESONANCE: <strong>{(avgWave * 100).toFixed(0)}%</strong></span>
        </span>
        <span className="text-foreground/40 font-mono">
          CORE_TEMP: 34°C &bull; CLOCK: 4.8 GHz
        </span>
        <span className="uppercase text-green-400 font-bold">
          {persona === "ev" ? "BIO_SYNC: 100%" : "APERTURE: LOCKED"}
        </span>
      </div>
    </div>
  );
};
