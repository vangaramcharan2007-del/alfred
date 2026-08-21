"use client";

import React, { useState, useRef, useEffect } from "react";
import { useJarvis } from "@/context/JarvisContext";
import { Terminal, Send, ChevronRight, Brain, Clock, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export const ActionTerminal: React.FC = () => {
  const { messages, submitCommand, aiState, persona } = useJarvis();
  const [inputVal, setInputVal] = useState("");
  const [expandedThoughtId, setExpandedThoughtId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, aiState]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    submitCommand(inputVal);
    setInputVal("");
  };

  const quickPrompts = [
    "Write Python script for cluster mesh scanning",
    "Calculate derivative of e^(2x)*cos(3x)",
    "What is the architecture of NANI master?",
    "Check GPU VRAM and system health",
  ];

  return (
    <div className="spatial-glass hud-bracket p-4 flex flex-col space-y-3 font-mono text-xs h-full min-h-[420px]">
      {/* Terminal Header */}
      <div className="flex items-center justify-between border-b border-primary/20 pb-2.5">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-primary" />
          <span className="font-bold text-foreground tracking-wider uppercase glow-primary">
            {persona === "ev" ? "NEURAL ACTION STREAM" : "TACTICAL MISSION TERMINAL"}
          </span>
        </div>
        <span className="text-[10px] text-foreground/40 font-bold">NODE: 100.105.164.83</span>
      </div>

      {/* Messages Stream */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[340px]"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-3 rounded space-y-2 transition-all ${
              msg.sender === "user"
                ? "bg-primary/10 border border-primary/30 ml-6"
                : "bg-black/50 border border-white/5 mr-2"
            }`}
          >
            {/* Meta */}
            <div className="flex items-center justify-between text-[10px] text-foreground/50">
              <span className="font-bold text-primary flex items-center gap-1.5 uppercase glow-primary">
                {msg.sender === "user" ? "CHARAN" : persona === "ev" ? "E.V. AI" : "ALFRED"}
              </span>
              <div className="flex items-center gap-2">
                {msg.nodeUsed && (
                  <span className="bg-black/60 px-1.5 py-0.5 rounded border border-white/10 text-foreground/70">
                    {msg.nodeUsed} ({msg.modelUsed})
                  </span>
                )}
                {msg.latency && (
                  <span className="text-green-400 flex items-center gap-0.5">
                    <Clock className="w-2.5 h-2.5" /> {msg.latency}s
                  </span>
                )}
                <span>{msg.timestamp}</span>
              </div>
            </div>

            {/* Message Body */}
            <div className="text-foreground/90 leading-relaxed whitespace-pre-wrap">
              {msg.text}
            </div>

            {/* Collapsible Chain-of-Thought */}
            {msg.thought && (
              <div className="pt-1">
                <button
                  onClick={() =>
                    setExpandedThoughtId(expandedThoughtId === msg.id ? null : msg.id)
                  }
                  className="flex items-center gap-1 text-[10px] text-primary/80 hover:text-primary transition-colors"
                >
                  <Brain className="w-3 h-3" />
                  <span>
                    {expandedThoughtId === msg.id ? "Hide Reasoning Process" : "View Chain-of-Thought"}
                  </span>
                </button>

                {expandedThoughtId === msg.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="mt-2 p-2.5 rounded bg-black/80 border border-primary/20 text-[10px] text-foreground/70 font-mono space-y-1 whitespace-pre-wrap"
                  >
                    <div className="text-primary font-bold text-[9px] uppercase tracking-wider">
                      &lt;thought&gt; Multi-Node Reasoning Trace
                    </div>
                    {msg.thought}
                  </motion.div>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Live Processing Indicator */}
        {aiState !== "IDLE" && (
          <div className="p-2.5 rounded bg-primary/10 border border-primary/40 flex items-center space-x-2 text-primary">
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
            <span className="text-[11px] font-bold uppercase tracking-wider animate-pulse">
              Jarvis is currently {aiState}...
            </span>
          </div>
        )}
      </div>

      {/* Quick Prompt Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[10px]">
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => submitCommand(p)}
            className="px-2.5 py-1 rounded bg-black/40 border border-white/5 hover:border-primary/40 hover:text-primary text-foreground/60 whitespace-nowrap transition-all flex items-center gap-1"
          >
            <ChevronRight className="w-2.5 h-2.5 text-primary" />
            <span>{p}</span>
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2 pt-1 border-t border-white/10">
        <div className="relative flex-1">
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder={`Instruct ${persona === "ev" ? "E.V." : "Alfred"}...`}
            className="w-full bg-black/60 border border-white/10 focus:border-primary px-3 py-2 rounded text-foreground placeholder-foreground/30 outline-none text-xs font-mono transition-all glow-box-primary"
          />
        </div>
        <button
          type="submit"
          disabled={aiState !== "IDLE" || !inputVal.trim()}
          className="px-4 py-2 bg-primary text-black font-bold rounded flex items-center gap-1.5 hover:opacity-90 transition-opacity disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
          <span>RUN</span>
        </button>
      </form>
    </div>
  );
};
