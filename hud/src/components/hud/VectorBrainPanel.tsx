"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Database, ShieldCheck, Sparkles, Binary } from "lucide-react";
import { motion } from "framer-motion";

export const VectorBrainPanel: React.FC = () => {
  const { totalVectors, vectorChunks, persona } = useJarvis();

  return (
    <div className="spatial-glass hud-bracket p-4 flex flex-col space-y-3.5 font-mono text-xs h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-primary/20 pb-2.5">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-primary" />
          <span className="font-bold text-foreground tracking-wider uppercase glow-primary">
            {persona === "ev" ? "CHROMADB NEURAL VECTORS" : "VECTOR MEMORY RETRIEVER"}
          </span>
        </div>
        <span className="text-[10px] text-primary font-bold px-2 py-0.5 rounded bg-primary/10 border border-primary/30 glow-box-primary">
          {totalVectors.toLocaleString()} CHUNKS
        </span>
      </div>

      {/* Vector Distribution Metrics */}
      <div className="grid grid-cols-2 gap-2">
        <div className="p-2.5 rounded bg-black/40 border border-white/5 space-y-1">
          <span className="text-[9px] text-foreground/50 uppercase">HYBRID SEARCH</span>
          <div className="text-xs font-bold text-foreground flex items-center justify-between">
            <span>BM25 + Dense</span>
            <Sparkles className="w-3 h-3 text-primary animate-pulse" />
          </div>
        </div>

        <div className="p-2.5 rounded bg-black/40 border border-white/5 space-y-1">
          <span className="text-[9px] text-foreground/50 uppercase">RETRIEVAL SPEED</span>
          <div className="text-xs font-bold text-green-400 flex items-center justify-between">
            <span>5.2 ms</span>
            <Binary className="w-3 h-3 text-green-400" />
          </div>
        </div>
      </div>

      {/* Memory Vector Chunks Feed */}
      <div className="space-y-2 overflow-y-auto max-h-[180px] pr-1">
        <div className="text-[9px] text-foreground/40 uppercase tracking-wider">
          Semantic Grounding Memory Chunks:
        </div>

        {vectorChunks.map((chunk) => (
          <motion.div
            key={chunk.id}
            whileHover={{ scale: 1.01 }}
            className="p-2 rounded bg-black/40 border border-white/5 hover:border-primary/40 transition-all space-y-1"
          >
            <div className="flex items-center justify-between text-[9px]">
              <span className="font-bold text-primary px-1 py-0.5 rounded bg-primary/10 border border-primary/20 uppercase">
                {chunk.category}
              </span>
              <span className="text-green-400 font-mono font-bold">
                SIMILARITY: {(chunk.score * 100).toFixed(0)}%
              </span>
            </div>

            <div className="text-[10px] text-foreground/80 leading-snug">
              {chunk.content}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Safety Gate Indicator */}
      <div className="mt-auto pt-2.5 border-t border-white/10 flex items-center justify-between text-[9px] text-foreground/60">
        <span className="flex items-center gap-1.5 text-green-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>PRODUCTION SAFETY GATE: ACTIVE</span>
        </span>
        <span className="text-foreground/40">CONFIRM GATED</span>
      </div>
    </div>
  );
};
