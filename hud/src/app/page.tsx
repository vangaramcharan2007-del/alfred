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
    <main className="min-h-screen flex flex-col relative bg-background bg-tech-grid overflow-hidden pb-24">
      {/* Background Ambient Glow Accents */}
      <div className="fixed top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-primary/10 rounded-full filter blur-[140px] pointer-events-none -z-10" />
      <div className="fixed -top-40 -right-40 w-[450px] h-[450px] bg-secondary/15 rounded-full filter blur-[120px] pointer-events-none -z-10" />

      {/* Top Spatial Glass Header */}
      <div className="p-4 pb-2 max-w-7xl w-full mx-auto">
        <Header />
      </div>

      {/* Main HUD Canvas Area */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-4 pt-2">
        <AnimatePresence mode="wait">
          {worldMonitorActive ? (
            /* =========================================================================
               WORLD MONITOR OVERLAY (GLOBAL SITUATION ROOM)
               ========================================================================= */
            <motion.div
              key="world-monitor"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              transition={{ duration: 0.4 }}
              className="w-full h-full min-h-[640px]"
            >
              <WorldSituationRoom />
            </motion.div>
          ) : (
            /* =========================================================================
               STANDARD PERSONA HUD (3-COLUMN SPATIAL GLASS LAYOUT)
               ========================================================================= */
            <motion.div
              key="standard-hud"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start"
            >
              {/* Left Column (4 cols): Cluster Radar & GPU Telemetry */}
              <div className="lg:col-span-4 space-y-5">
                <MeshClusterRadar />
              </div>

              {/* Center Column (4 cols): Core Aperture & Reticle */}
              <div className="lg:col-span-4 flex flex-col items-center space-y-5">
                <CoreAperture />
                <div className="w-full">
                  <VectorBrainPanel />
                </div>
              </div>

              {/* Right Column (4 cols): Action Terminal & Live Intent Stream */}
              <div className="lg:col-span-4 space-y-5">
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
