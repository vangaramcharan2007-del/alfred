"use client";

import React from "react";
import { useJarvis } from "@/context/JarvisContext";
import { AIState } from "@/types/hud";
import { Settings, Sparkles, Shield, Radio, Flame } from "lucide-react";

export const DevControlStrip: React.FC = () => {
  const {
    persona,
    setPersona,
    aiState,
    setAiState,
    worldMonitorActive,
    toggleWorldMonitor,
    triggerAudioPing,
    submitCommand,
  } = useJarvis();

  const states: AIState[] = ["IDLE", "LISTENING", "THINKING", "EXECUTING", "WORLD_MONITOR_ACTIVE"];

  return (
    <aside aria-label="Dev controls" className="fixed bottom-3 inset-x-4 max-w-7xl mx-auto spatial-glass hud-bracket p-2.5 px-4 flex flex-wrap items-center justify-between gap-3 z-40 border border-primary/40 font-mono text-xs shadow-2xl">
      {/* Persona Toggle Controls */}
      <div className="flex items-center space-x-2">
        <span className="text-[10px] text-foreground/50 font-bold uppercase tracking-wider flex items-center gap-1">
          <Settings className="w-3.5 h-3.5 text-primary" /> PERSONA:
        </span>
        <div className="flex items-center p-0.5 rounded bg-black/60 border border-white/10">
          <button
            onClick={() => setPersona("ev")}
            className={`px-2.5 py-1 rounded text-[10px] font-bold transition-all flex items-center gap-1 ${
              persona === "ev"
                ? "bg-primary text-black shadow-md glow-box-primary"
                : "text-foreground/60 hover:text-foreground"
            }`}
          >
            <Sparkles className="w-3 h-3" />
            <span>E.V. (CYBER)</span>
          </button>
          <button
            onClick={() => setPersona("alfred")}
            className={`px-2.5 py-1 rounded text-[10px] font-bold transition-all flex items-center gap-1 ${
              persona === "alfred"
                ? "bg-primary text-black shadow-md glow-box-primary"
                : "text-foreground/60 hover:text-foreground"
            }`}
          >
            <Shield className="w-3 h-3" />
            <span>ALFRED (TACTICAL)</span>
          </button>
        </div>
      </div>

      {/* AI State Controls */}
      <div className="flex items-center space-x-2">
        <span className="text-[10px] text-foreground/50 font-bold uppercase tracking-wider hidden sm:inline">
          AI STATE:
        </span>
        <div className="flex items-center p-0.5 rounded bg-black/60 border border-white/10 gap-0.5 overflow-x-auto">
          {states.map((s) => (
            <button
              key={s}
              onClick={() => {
                setAiState(s);
                if (s === "WORLD_MONITOR_ACTIVE") {
                  if (!worldMonitorActive) toggleWorldMonitor();
                }
              }}
              className={`px-2.5 py-1 rounded text-[9px] font-bold transition-all whitespace-nowrap ${
                aiState === s
                  ? "bg-primary text-black glow-box-primary font-black"
                  : "text-foreground/60 hover:text-foreground"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Action Triggers */}
      <div className="flex items-center space-x-2">
        <button
          onClick={triggerAudioPing}
          className="px-2.5 py-1 rounded bg-black/60 hover:bg-primary/20 text-primary border border-primary/40 font-bold transition-all text-[10px] flex items-center gap-1"
        >
          <Radio className="w-3 h-3" />
          <span>SIMULATE VOICE</span>
        </button>

        <button
          onClick={() => submitCommand("Deploy Coding Swarm for cluster optimization")}
          className="px-2.5 py-1 rounded bg-primary/20 hover:bg-primary/30 text-primary border border-primary/50 font-bold transition-all text-[10px] flex items-center gap-1 glow-box-primary"
        >
          <Flame className="w-3 h-3" />
          <span>DEPLOY SWARM</span>
        </button>
      </div>
    </aside>
  );
};
