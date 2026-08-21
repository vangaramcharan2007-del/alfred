"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Server, Activity, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export const MeshClusterRadar: React.FC = () => {
  const { meshNodes, persona } = useJarvis();

  return (
    <div className="spatial-glass hud-bracket p-4 flex flex-col space-y-3.5 font-mono text-xs h-full">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-primary/20 pb-2.5">
        <div className="flex items-center space-x-2">
          <Server className="w-4 h-4 text-primary" />
          <span className="font-bold text-foreground tracking-wider uppercase glow-primary">
            {persona === "ev" ? "NEURAL MESH CLUSTER" : "TACTICAL NODE RADAR"}
          </span>
        </div>
        <span className="px-2 py-0.5 rounded text-[9px] bg-green-500/20 text-green-400 font-bold border border-green-500/30 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-ping" />
          5 NODES LINKED
        </span>
      </div>

      {/* Circular Radar Plot Canvas */}
      <div className="relative w-full aspect-[2/1] rounded bg-black/60 border border-primary/20 overflow-hidden flex items-center justify-center">
        {/* Subtle Tech Grid Mask */}
        <div className="absolute inset-0 bg-tech-grid opacity-20" />

        {/* Radar Concentric Rings */}
        <div className="absolute w-40 h-40 rounded-full border border-primary/20" />
        <div className="absolute w-28 h-28 rounded-full border border-primary/30" />
        <div className="absolute w-14 h-14 rounded-full border border-primary/40" />

        {/* Crosshair Lines */}
        <div className="absolute inset-x-0 h-px bg-primary/20" />
        <div className="absolute inset-y-0 w-px bg-primary/20" />

        {/* Radar Sweep Line */}
        <div className="absolute inset-0 origin-center animate-radar-sweep pointer-events-none">
          <div className="w-1/2 h-1/2 bg-gradient-to-br from-primary/30 to-transparent origin-bottom-right" />
        </div>

        {/* 5 Plotted Cluster Nodes with Live Pings */}
        <div className="absolute top-[22%] left-[22%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse glow-box-primary" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 group-hover:text-primary">
            NANI (12ms)
          </span>
        </div>

        <div className="absolute top-[32%] right-[20%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse glow-box-primary" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 group-hover:text-primary">
            W1: 4050 (44ms)
          </span>
        </div>

        <div className="absolute bottom-[24%] right-[32%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse glow-box-primary" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 group-hover:text-primary">
            W3: 5050 (58ms)
          </span>
        </div>

        <div className="absolute bottom-[20%] left-[28%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse glow-box-primary" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 group-hover:text-primary">
            W4: TUF (65ms)
          </span>
        </div>

        <div className="absolute top-[60%] left-[58%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse glow-box-primary" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 group-hover:text-primary">
            W5: 5060 (38ms)
          </span>
        </div>
      </div>

      {/* Floating Node Cards Telemetry List */}
      <div className="space-y-2 overflow-y-auto max-h-[320px] pr-1">
        {meshNodes.map((node) => (
          <motion.div
            key={node.id}
            whileHover={{ scale: 1.01 }}
            className="p-2.5 rounded bg-black/40 border border-white/5 hover:border-primary/40 transition-all space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="font-bold text-foreground text-[11px]">{node.name}</span>
              </div>
              <span className="text-[10px] text-primary font-bold">{node.latencyMs}ms</span>
            </div>

            <div className="flex items-center justify-between text-[10px] text-foreground/60">
              <span>{node.hardware}</span>
              <span className="text-foreground/80 font-mono">{node.vram}</span>
            </div>

            {/* Compute Load Bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-[8px] text-foreground/40">
                <span>GPU COMPUTE LOAD</span>
                <span>{node.loadPercent}%</span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  style={{ width: `${node.loadPercent}%` }}
                  className="h-full bg-primary glow-box-primary"
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
