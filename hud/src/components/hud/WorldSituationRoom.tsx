"use client";

import React, { useState } from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Globe, Radio, Video, Satellite, X } from "lucide-react";

export const WorldSituationRoom: React.FC = () => {
  const { threatPings, intelFeed, toggleWorldMonitor, persona } = useJarvis();
  const [selectedPing, setSelectedPing] = useState(threatPings[3]); // Default to Bengaluru Master Node

  return (
    <div className="w-full h-full glass-panel p-6 flex flex-col space-y-4 font-mono text-xs relative overflow-hidden animate-fadeIn">
      {/* Top Header Bar of Situation Room */}
      <div className="flex items-center justify-between border-b border-primary/20 pb-3 z-10">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded bg-red-500/20 border border-red-500/40 text-red-400 glow-box">
            <Globe className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-black tracking-widest text-foreground glow-text uppercase">
                GLOBAL SITUATION ROOM &bull; WORLD MONITOR
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 font-bold border border-red-500/30 animate-pulse">
                DEFCON 2 MONITORING
              </span>
            </div>
            <p className="text-[10px] text-foreground/60">
              ORBITAL SATELLITE TELEMETRY &bull; TAILSCALE MESH SURVEILLANCE
            </p>
          </div>
        </div>

        <button
          onClick={toggleWorldMonitor}
          className="p-2 rounded bg-white/5 hover:bg-white/15 text-foreground/70 hover:text-primary transition-all border border-white/10"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Main Grid: 70% Left World Map | 30% Right Tactical Feeds */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-[500px]">
        {/* =========================================================================
            LEFT 70% (8 COLS): Dark High-Tech SVG World Map Canvas
           ========================================================================= */}
        <div className="lg:col-span-8 glass-panel-subtle p-4 flex flex-col relative rounded border border-primary/20 bg-black/60 overflow-hidden group">
          {/* Map Grid Background */}
          <div className="absolute inset-0 bg-tech-grid opacity-30 pointer-events-none" />

          {/* Latitude / Longitude Overlay Lines */}
          <div className="absolute inset-0 flex justify-between pointer-events-none opacity-20">
            <div className="border-r border-primary/30 w-1/4 h-full" />
            <div className="border-r border-primary/30 w-1/4 h-full" />
            <div className="border-r border-primary/30 w-1/4 h-full" />
            <div className="border-r border-primary/30 w-1/4 h-full" />
          </div>

          {/* High-Tech Vector World Map SVG */}
          <div className="relative flex-1 flex items-center justify-center min-h-[360px]">
            <svg
              className="w-full h-full max-h-[460px] opacity-85"
              viewBox="0 0 1000 500"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <radialGradient id="pingGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0" />
                </radialGradient>
              </defs>

              {/* Simplified Dark Continents Vector Path */}
              <g fill="#1a1e24" stroke="rgba(255,255,255,0.08)" strokeWidth="0.8">
                {/* North America */}
                <path d="M120 80 Q 200 60 280 110 T 320 220 Q 220 250 180 200 T 110 140 Z" />
                {/* South America */}
                <path d="M260 260 Q 320 280 340 380 T 290 480 Q 240 420 250 320 Z" />
                {/* Europe */}
                <path d="M460 70 Q 560 60 580 140 T 480 180 Q 440 130 460 70 Z" />
                {/* Africa */}
                <path d="M470 190 Q 580 200 560 340 T 500 420 Q 430 320 460 220 Z" />
                {/* Asia */}
                <path d="M590 60 Q 820 50 880 190 T 720 280 Q 620 240 590 120 Z" />
                {/* Australia */}
                <path d="M780 320 Q 880 330 870 420 T 780 410 Q 740 360 780 320 Z" />
              </g>

              {/* Orbital Arc Vectors */}
              <path
                d="M 200 150 Q 500 40 730 200"
                stroke="var(--color-primary)"
                strokeWidth="1.2"
                strokeDasharray="6 4"
                className="opacity-40 animate-pulse"
              />
              <path
                d="M 300 350 Q 550 250 800 360"
                stroke="var(--color-secondary)"
                strokeWidth="1.2"
                strokeDasharray="4 6"
                className="opacity-40"
              />

              {/* Dynamic Geo-Pings plotted on Map */}
              {threatPings.map((ping) => {
                // Approximate Lat/Lng projection to 1000x500 SVG
                const x = ((ping.lng + 180) / 360) * 920 + 40;
                const y = ((90 - ping.lat) / 180) * 440 + 30;

                const isSelected = selectedPing.id === ping.id;

                return (
                  <g
                    key={ping.id}
                    onClick={() => setSelectedPing(ping)}
                    className="cursor-pointer group/pin"
                  >
                    {/* Outer Pulsing Wave */}
                    <circle
                      cx={x}
                      cy={y}
                      r={isSelected ? "18" : "10"}
                      fill="url(#pingGlow)"
                      className="animate-ping opacity-60"
                    />

                    {/* Pin Ring */}
                    <circle
                      cx={x}
                      cy={y}
                      r={isSelected ? "6" : "3.5"}
                      fill={isSelected ? "var(--color-primary)" : "#22c55e"}
                      stroke="#000"
                      strokeWidth="1"
                    />

                    {/* Tag label */}
                    <text
                      x={x + 10}
                      y={y + 4}
                      fill="var(--color-fg)"
                      fontSize="9"
                      fontFamily="monospace"
                      className="opacity-80 group-hover/pin:opacity-100 font-bold"
                    >
                      {ping.name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Selected Pin Info Card (Overlay on Bottom of Map) */}
          <div className="mt-auto p-3 rounded bg-black/80 border border-white/10 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse glow-box" />
              <div>
                <span className="text-[10px] text-foreground/50 uppercase">TARGET VECTOR:</span>
                <div className="font-bold text-foreground text-sm">{selectedPing.name}</div>
              </div>
            </div>

            <div className="flex items-center space-x-4 text-[10px]">
              <div>
                <span className="text-foreground/50">COORDINATES:</span>
                <div className="text-primary font-bold">{selectedPing.lat}°N, {selectedPing.lng}°E</div>
              </div>
              <div>
                <span className="text-foreground/50">STATUS:</span>
                <div className="text-green-400 font-bold">{selectedPing.status}</div>
              </div>
              <div className="px-2 py-1 rounded bg-red-500/20 text-red-400 border border-red-500/30 font-bold">
                {selectedPing.threatLevel}
              </div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            RIGHT 30% (4 COLS): 3 Tactical Feed Blocks (Sat Feeds & Video Feeds)
           ========================================================================= */}
        <div className="lg:col-span-4 flex flex-col space-y-4">
          {/* Feed Block 1: Live Video / Broadcast Monitor (like screenshot) */}
          <div className="glass-panel-subtle p-3 rounded border border-white/10 space-y-2 bg-black/60">
            <div className="flex items-center justify-between text-[10px] text-foreground/70">
              <span className="flex items-center gap-1.5 text-primary font-bold uppercase">
                <Video className="w-3.5 h-3.5" /> LIVE SATELLITE BROADCAST
              </span>
              <span className="text-red-500 animate-pulse font-bold">&bull; REC</span>
            </div>

            {/* Video Placeholder Container with scanlines */}
            <div className="relative w-full aspect-video rounded bg-zinc-900 border border-white/10 overflow-hidden flex items-center justify-center">
              <div className="absolute inset-0 scanline-overlay pointer-events-none opacity-40" />
              <div className="text-center p-4 space-y-1">
                <Radio className="w-6 h-6 text-primary mx-auto animate-pulse" />
                <span className="text-[10px] text-foreground/70 font-bold tracking-wider">
                  GEO-STATIONARY ORBIT FEED 04
                </span>
                <p className="text-[8px] text-foreground/40 font-mono">
                  RESOLUTION: 4K &bull; BITRATE: 120 MBPS &bull; QUANTUM CRYPTO
                </p>
              </div>
            </div>
          </div>

          {/* Feed Block 2: Global Cyber Intel Stream */}
          <div className="glass-panel-subtle p-3 rounded border border-white/10 space-y-2 bg-black/60 flex-1 flex flex-col">
            <div className="flex items-center justify-between text-[10px] text-foreground/70 border-b border-white/10 pb-1.5">
              <span className="flex items-center gap-1.5 text-primary font-bold uppercase">
                <Satellite className="w-3.5 h-3.5" /> TACTICAL INTEL LOGS
              </span>
              <span className="text-green-400 font-bold">REAL-TIME</span>
            </div>

            <div className="space-y-2 overflow-y-auto max-h-[160px] pr-1">
              {intelFeed.map((item) => (
                <div
                  key={item.id}
                  className="p-2 rounded bg-black/40 border border-white/5 text-[10px] space-y-1"
                >
                  <div className="flex items-center justify-between text-[9px] text-foreground/50">
                    <span className="text-primary font-bold">[{item.category}]</span>
                    <span>{item.timestamp}</span>
                  </div>
                  <div className="text-foreground/90 leading-snug">{item.title}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* =========================================================================
          BOTTOM SCROLLING INTELLIGENCE TICKER
         ========================================================================= */}
      <div className="w-full bg-black/80 border border-primary/30 p-2 rounded overflow-hidden flex items-center gap-3">
        <span className="px-2 py-0.5 bg-primary text-black font-black text-[9px] rounded uppercase tracking-wider whitespace-nowrap">
          INTEL TICKER
        </span>
        <div className="overflow-hidden relative flex-1">
          <div className="whitespace-nowrap flex gap-8 animate-marquee text-[10px] text-foreground/80 font-mono">
            <span>&bull; MESH CLUSTER: 5/5 GPU NODES ONLINE</span>
            <span>&bull; MASTER NANI NODE: INTEL IRIS XE RUNNING STT/TTS ENGINE</span>
            <span>&bull; WORKER 1: RTX 4050 DEPLOYED FOR CODE SWARM</span>
            <span>&bull; WORKER 3: RTX 5050 RUNNING DEEPSEEK-R1:14B MATHEMATICAL REASONING</span>
            <span>&bull; WORKER 5: RTX 5060 STANDBY FOR VECTOR ACCELERATION</span>
            <span>&bull; CHROMADB: 2,736 VECTOR CHUNKS SYNCHRONIZED ACROSS HYBRID BRAIN</span>
          </div>
        </div>
      </div>
    </div>
  );
};
