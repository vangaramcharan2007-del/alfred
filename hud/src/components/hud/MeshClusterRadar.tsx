"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Server } from "lucide-react";
import { motion } from "framer-motion";

export const MeshClusterRadar: React.FC = () => {
  const { meshNodes, persona } = useJarvis();

  return (
    <div className="glass-panel p-4 flex flex-col space-y-4 font-mono text-xs h-full">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-primary/20 pb-2.5">
        <div className="flex items-center space-x-2">
          <Server className="w-4 h-4 text-primary" />
          <span className="font-bold text-foreground tracking-wider uppercase">
            {persona === "ev" ? "NEURAL MESH CLUSTER" : "TACTICAL NODE RADAR"}
          </span>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] bg-green-500/20 text-green-400 font-bold border border-green-500/30 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-ping" />
          5/5 SYNCED
        </span>
      </div>

      {/* Circular Radar Plot Canvas */}
      <div className="relative w-full aspect-[2/1] rounded bg-black/50 border border-white/10 overflow-hidden flex items-center justify-center">
        {/* Radar Rings */}
        <div className="absolute w-36 h-36 rounded-full border border-primary/20" />
        <div className="absolute w-24 h-24 rounded-full border border-primary/30" />
        <div className="absolute w-12 h-12 rounded-full border border-primary/40" />

        {/* Crosshair Lines */}
        <div className="absolute inset-x-0 h-px bg-primary/20" />
        <div className="absolute inset-y-0 w-px bg-primary/20" />

        {/* Radar Sweep Line */}
        <div className="absolute inset-0 origin-center animate-radar-sweep pointer-events-none">
          <div className="w-1/2 h-1/2 bg-gradient-to-br from-primary/25 to-transparent origin-bottom-right" />
        </div>

        {/* 5 Plotted Cluster Nodes */}
        <div className="absolute top-[20%] left-[25%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse glow-box" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 opacity-80 group-hover:opacity-100">
            NANI (12ms)
          </span>
        </div>

        <div className="absolute top-[35%] right-[22%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse glow-box" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 opacity-80 group-hover:opacity-100">
            W1: 4050 (44ms)
          </span>
        </div>

        <div className="absolute bottom-[25%] right-[35%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse glow-box" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 opacity-80 group-hover:opacity-100">
            W3: 5050 (58ms)
          </span>
        </div>

        <div className="absolute bottom-[20%] left-[30%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse glow-box" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 opacity-80 group-hover:opacity-100">
            W4: TUF (65ms)
          </span>
        </div>

        <div className="absolute top-[60%] left-[60%] flex items-center gap-1 group cursor-pointer">
          <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse glow-box" />
          <span className="text-[9px] bg-black/80 px-1 py-0.5 rounded border border-white/10 text-foreground/80 opacity-80 group-hover:opacity-100">
            W5: 5060 (38ms)
          </span>
        </div>
      </div>

      {/* Node Cards Telemetry List */}
      <div className="space-y-2.5 overflow-y-auto max-h-[300px] pr-1">
        {meshNodes.map((node) => (
          <motion.div
            key={node.id}
            whileHover={{ scale: 1.01 }}
            className="p-2.5 rounded bg-black/40 border border-white/10 hover:border-primary/40 transition-all space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="font-bold text-foreground text-[11px]">{node.name}</span>
              </div>
              <span className="text-[10px] text-primary/90 font-bold">{node.latencyMs}ms</span>
            </div>

            <div className="flex items-center justify-between text-[10px] text-foreground/70">
              <span>{node.hardware}</span>
              <span className="text-foreground/90 font-mono">{node.vram}</span>
            </div>

            {/* Load Meter Bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-[9px] text-foreground/50">
                <span>GPU COMPUTE LOAD</span>
                <span>{node.loadPercent}%</span>
              </div>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div
                  style={{ width: `${node.loadPercent}%` }}
                  className="h-full bg-primary glow-box"
                />
              </div>
            </div>

            <div className="text-[9px] text-primary/80 truncate">
              Models: {node.models.join(", ")}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
