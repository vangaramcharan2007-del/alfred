"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Database, ShieldCheck, Sparkles, Binary } from "lucide-react";
import { motion } from "framer-motion";

export const VectorBrainPanel: React.FC = () => {
  const { totalVectors, vectorChunks, persona } = useJarvis();

  return (
    <div className="glass-panel p-4 flex flex-col space-y-4 font-mono text-xs h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-primary/20 pb-2.5">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-primary" />
          <span className="font-bold text-foreground tracking-wider uppercase">
            {persona === "ev" ? "CHROMADB NEURAL VECTORS" : "VECTOR MEMORY RETRIEVER"}
          </span>
        </div>
        <span className="text-[10px] text-primary font-bold px-2 py-0.5 rounded bg-primary/10 border border-primary/30">
          {totalVectors.toLocaleString()} CHUNKS
        </span>
      </div>

      {/* Vector Distribution Metrics */}
      <div className="grid grid-cols-2 gap-2">
        <div className="p-2.5 rounded bg-black/40 border border-white/10 space-y-1">
          <span className="text-[10px] text-foreground/60 uppercase">HYBRID SEARCH</span>
          <div className="text-sm font-bold text-foreground flex items-center justify-between">
            <span>BM25 + Dense</span>
            <Sparkles className="w-3.5 h-3.5 text-primary animate-pulse" />
          </div>
        </div>

        <div className="p-2.5 rounded bg-black/40 border border-white/10 space-y-1">
          <span className="text-[10px] text-foreground/60 uppercase">RETRIEVAL LATENCY</span>
          <div className="text-sm font-bold text-green-400 flex items-center justify-between">
            <span>5.2 ms</span>
            <Binary className="w-3.5 h-3.5 text-green-400" />
          </div>
        </div>
      </div>

      {/* Memory Vector Chunks Feed */}
      <div className="space-y-2.5 overflow-y-auto max-h-[300px] pr-1">
        <div className="text-[10px] text-foreground/50 uppercase tracking-wider">
          Recent Semantic Grounding Context:
        </div>

        {vectorChunks.map((chunk) => (
          <motion.div
            key={chunk.id}
            whileHover={{ scale: 1.01 }}
            className="p-2.5 rounded bg-black/50 border border-white/10 hover:border-primary/40 transition-all space-y-1.5"
          >
            <div className="flex items-center justify-between text-[10px]">
              <span className="font-bold text-primary px-1.5 py-0.5 rounded bg-primary/15 border border-primary/30 uppercase">
                {chunk.category}
              </span>
              <span className="text-green-400 font-mono font-bold">
                SIMILARITY: {(chunk.score * 100).toFixed(0)}%
              </span>
            </div>

            <div className="text-[11px] text-foreground/80 leading-snug">
              {chunk.content}
            </div>

            <div className="text-[9px] text-foreground/40 truncate">
              Source: {chunk.source}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Safety Gate Indicator */}
      <div className="mt-auto pt-3 border-t border-white/10 flex items-center justify-between text-[10px] text-foreground/70">
        <span className="flex items-center gap-1.5 text-green-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>PRODUCTION SAFETY GATE: ACTIVE</span>
        </span>
        <span className="text-foreground/50">CONFIRM GATED</span>
      </div>
    </div>
  );
};
