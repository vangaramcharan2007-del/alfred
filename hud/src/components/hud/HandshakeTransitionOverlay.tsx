"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useJarvis } from "@/context/JarvisContext";
import { ShieldAlert, Zap, Terminal } from "lucide-react";

export const HandshakeTransitionOverlay: React.FC = () => {
  const { isHandshaking, persona } = useJarvis();

  return (
    <AnimatePresence>
      {isHandshaking && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/95 backdrop-blur-3xl overflow-hidden font-mono"
        >
          {/* Scanline & Glitch bars */}
          <div className="absolute inset-0 scanline-overlay pointer-events-none opacity-40" />
          <motion.div
            initial={{ scaleY: 0 }}
            animate={{ scaleY: [0, 1.2, 1] }}
            exit={{ scaleY: 0 }}
            transition={{ duration: 0.4 }}
            className="absolute inset-x-0 h-1 bg-primary glow-box top-1/2 -translate-y-1/2"
          />

          <div className="relative z-10 flex flex-col items-center max-w-lg p-8 text-center space-y-6">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
              className="p-4 rounded-full border border-primary/40 bg-primary/10 glow-box"
            >
              {persona === "ev" ? (
                <ShieldAlert className="w-12 h-12 text-primary animate-pulse" />
              ) : (
                <Zap className="w-12 h-12 text-primary animate-pulse" />
              )}
            </motion.div>

            <div className="space-y-2">
              <div className="text-xs uppercase tracking-[0.4em] text-primary/80 font-bold flex items-center justify-center gap-2">
                <Terminal className="w-4 h-4" /> Protocol Handshake In Progress
              </div>
              <h2 className="text-2xl font-black tracking-widest text-foreground glow-text uppercase">
                {persona === "ev"
                  ? "CALIBRATING WAYNE-TECH TACTICAL GRID"
                  : "INITIALIZING CYBERNETIC NEURAL LAB"}
              </h2>
            </div>

            <div className="w-full bg-black/60 border border-white/10 p-3 rounded text-left text-xs text-primary/90 space-y-1">
              <div className="flex justify-between">
                <span>&gt; AUTH_KEY: SHA-512 VERIFIED</span>
                <span className="text-green-400">100%</span>
              </div>
              <div className="flex justify-between">
                <span>&gt; RE-ROUTING GPU MESH TOPOLOGY</span>
                <span className="text-primary animate-pulse">SYNCING</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>&gt; RE-INDEXING 2,736 CHROMADB VECTORS</span>
                <span className="text-green-400">OK</span>
              </div>
            </div>

            <div className="w-64 h-1.5 bg-white/10 rounded-full overflow-hidden border border-primary/30">
              <motion.div
                initial={{ width: "0%" }}
                animate={{ width: "100%" }}
                transition={{ duration: 1.1, ease: "easeInOut" }}
                className="h-full bg-primary glow-box"
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
