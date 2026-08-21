"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Header } from "@/components/layout/Header";
import { DevControlStrip } from "@/components/layout/DevControlStrip";
import { CoreAperture } from "@/components/hud/CoreAperture";
import { MeshClusterRadar } from "@/components/hud/MeshClusterRadar";
import { ActionTerminal } from "@/components/hud/ActionTerminal";
import { VectorBrainPanel } from "@/components/hud/VectorBrainPanel";
import { WorldSituationRoom } from "@/components/hud/WorldSituationRoom";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const { worldMonitorActive } = useJarvis();

  return (
    <main className="min-h-screen flex flex-col relative bg-background overflow-hidden pb-24 selection:bg-primary selection:text-black font-mono">
      {/* Background Ambient Quantum Gradients */}
      <div className="fixed top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-primary/10 rounded-full filter blur-[160px] pointer-events-none -z-10" />
      <div className="fixed -top-40 -right-40 w-[550px] h-[550px] bg-secondary/15 rounded-full filter blur-[140px] pointer-events-none -z-10" />
      <div className="fixed -bottom-40 -left-40 w-[550px] h-[550px] bg-primary/10 rounded-full filter blur-[140px] pointer-events-none -z-10" />

      {/* Top Floating Spatial Glass Header */}
      <div className="p-4 pb-2 max-w-[1600px] w-full mx-auto">
        <Header />
      </div>

      {/* Main HUD Canvas Area (Cinematic Spatial Layout) */}
      <div className="flex-1 max-w-[1600px] w-full mx-auto p-4 pt-1">
        <AnimatePresence mode="wait">
          {worldMonitorActive ? (
            /* =========================================================================
               WORLD MONITOR OVERLAY (GLOBAL SITUATION ROOM)
               ========================================================================= */
            <motion.div
              key="world-monitor"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.97 }}
              transition={{ duration: 0.4 }}
              className="w-full h-full min-h-[660px]"
            >
              <WorldSituationRoom />
            </motion.div>
          ) : (
            /* =========================================================================
               STANDARD PERSONA HUD (PROPORTIONED SPATIAL GLASS GRID)
               ========================================================================= */
            <motion.div
              key="standard-hud"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start"
            >
              {/* Left Wing (3 cols): Cluster Node Telemetry & Radar */}
              <div className="lg:col-span-3 space-y-4">
                <MeshClusterRadar />
              </div>

              {/* Center Stage (5 cols): MASSIVE FOCAL AI CORE & VECTOR BRAIN */}
              <div className="lg:col-span-5 flex flex-col items-center space-y-4">
                <CoreAperture />
                <div className="w-full">
                  <VectorBrainPanel />
                </div>
              </div>

              {/* Right Wing (4 cols): Action Stream Terminal & Mission Dispatch */}
              <div className="lg:col-span-4 space-y-4">
                <ActionTerminal />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Fixed Bottom Dev Control Strip */}
      <DevControlStrip />
    </main>
  );
}
