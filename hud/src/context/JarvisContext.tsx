"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { Persona, AIState, MeshNode, IntelItem, ThreatPing, DialogueMessage, VectorChunk } from "@/types/hud";

interface JarvisContextType {
  persona: Persona;
  setPersona: (p: Persona) => void;
  togglePersona: () => void;
  aiState: AIState;
  setAiState: (s: AIState) => void;
  isHandshaking: boolean;
  audioWaveforms: number[];
  meshNodes: MeshNode[];
  intelFeed: IntelItem[];
  threatPings: ThreatPing[];
  messages: DialogueMessage[];
  vectorChunks: VectorChunk[];
  totalVectors: number;
  activeCommand: string;
  submitCommand: (cmd: string) => Promise<void>;
  triggerAudioPing: () => void;
  worldMonitorActive: boolean;
  toggleWorldMonitor: () => void;
}

const INITIAL_NODES: MeshNode[] = [
  {
    id: "nani-master",
    name: "NANI Master Node",
    role: "Core Controller & RAG",
    hardware: "Intel Iris Xe",
    ip: "100.105.164.83",
    status: "online",
    vram: "Shared 16GB System RAM",
    models: ["jarvis:latest", "qwen2.5-coder:1.5b", "qwen2.5-coder:7b"],
    latencyMs: 12,
    loadPercent: 18,
  },
  {
    id: "worker-1-4050",
    name: "Worker 1 (tuf-a16)",
    role: "Code Generation Swarm",
    hardware: "NVIDIA GeForce RTX 4050",
    ip: "100.77.90.36",
    status: "online",
    vram: "6GB GDDR6",
    models: ["deepseek-r1:1.5b", "qwen2.5-coder:1.5b", "qwen2.5-coder:7b"],
    latencyMs: 44,
    loadPercent: 32,
  },
  {
    id: "worker-3-5050",
    name: "Worker 3 (laptop-lafr0e5l)",
    role: "Heavy Deep Reasoning",
    hardware: "NVIDIA GeForce RTX 5050",
    ip: "100.81.36.31",
    status: "online",
    vram: "8GB GDDR7",
    models: ["deepseek-r1:14b", "deepseek-r1:1.5b"],
    latencyMs: 58,
    loadPercent: 74,
  },
  {
    id: "worker-4-tuf",
    name: "Worker 4 (ASUS TUF)",
    role: "Auxiliary Neural Compute",
    hardware: "NVIDIA RTX 3050 (16GB RAM)",
    ip: "100.94.12.88",
    status: "online",
    vram: "4GB GDDR6",
    models: ["qwen2.5-coder:7b-instruct"],
    latencyMs: 65,
    loadPercent: 21,
  },
  {
    id: "worker-5-5060",
    name: "Worker 5 (Blackwell Beast)",
    role: "Ultra-Fast Math & Logic",
    hardware: "NVIDIA GeForce RTX 5060",
    ip: "100.112.45.19",
    status: "online",
    vram: "8GB GDDR7",
    models: ["deepseek-r1:14b", "qwen2.5-coder:7b-instruct"],
    latencyMs: 38,
    loadPercent: 55,
  },
];

const INITIAL_INTEL: IntelItem[] = [
  {
    id: "int-1",
    timestamp: "19:54:12",
    category: "CLUSTER",
    severity: "INFO",
    title: "Mesh node 'Worker 1 (RTX 4050)' synchronized over Tailscale encrypted tunnel",
    source: "NANI_KERNEL",
  },
  {
    id: "int-2",
    timestamp: "19:53:48",
    category: "SECURITY",
    severity: "INFO",
    title: "Sandboxed tool execution verified by ProductionSafetyGate (CONFIRM level enforced)",
    source: "GUARDRAIL",
  },
  {
    id: "int-3",
    timestamp: "19:52:30",
    category: "INTEL",
    severity: "WARN",
    title: "Autonomous Web Agent verified 2,736 ChromaDB vector embeddings across memory store",
    source: "RAG_RETRIEVER",
  },
  {
    id: "int-4",
    timestamp: "19:51:04",
    category: "SATELLITE",
    severity: "INFO",
    title: "Telemetry uplink stable. 5 GPU nodes active across distributed cluster mesh",
    source: "MESH_ROUTER",
  },
];

const THREAT_PINGS: ThreatPing[] = [
  { id: "tp-1", name: "Tokyo Sector 7 Node", lat: 35.6762, lng: 139.6503, threatLevel: "ELEVATED", vector: "Telemetry Relay Delta", status: "STABLE" },
  { id: "tp-2", name: "Frankfurt Cyber-Hub", lat: 50.1109, lng: 8.6821, threatLevel: "HIGH", vector: "Encrypted Data Burst", status: "MONITORING" },
  { id: "tp-3", name: "Silicon Valley Gateway", lat: 37.3861, lng: -122.0839, threatLevel: "CRITICAL", vector: "Quantum Tunnel Ingestion", status: "LOCKED" },
  { id: "tp-4", name: "Bengaluru Master Mesh", lat: 12.9716, lng: 77.5946, threatLevel: "ELEVATED", vector: "Core NANI Node (Charan)", status: "ACTIVE" },
  { id: "tp-5", name: "London Satellite Link", lat: 51.5074, lng: -0.1278, threatLevel: "ELEVATED", vector: "Global Proxy Route", status: "STABLE" },
];

const INITIAL_MESSAGES: DialogueMessage[] = [
  {
    id: "msg-0",
    sender: "jarvis",
    text: "Good evening, Charan. All 5 cluster GPU nodes are linked over Tailscale. Memory database synchronized with 2,736 vectors. Standing by for command.",
    thought: "1. Verified local Master NANI health.\n2. Probed Worker 1 (RTX 4050), Worker 3 (RTX 5050), Worker 4, and Worker 5.\n3. Formulated ready posture.",
    timestamp: "19:50:00",
    nodeUsed: "NANI Master",
    modelUsed: "jarvis:latest",
    latency: 0.04,
  },
];

const INITIAL_VECTORS: VectorChunk[] = [
  { id: "v-1", source: "jarvis_core_identity", content: "User Profile: Charan is the sovereign architect & creator of Jarvis X.", score: 0.98, category: "IDENTITY" },
  { id: "v-2", source: "core_workers", content: "Worker 3: RTX 5050 GPU (8GB GDDR7) dedicated for deep mathematical Chain-of-Thought (deepseek-r1:14b).", score: 0.94, category: "CLUSTER" },
  { id: "v-3", source: "core_voice", content: "Voice Engine: Multi-threaded SAPI SpVoice + PowerShell System.Speech zero-dependency audio synthesis.", score: 0.91, category: "VOICE" },
  { id: "v-4", source: "code_mesh_router", content: "MeshRouter dynamically probes workers in 0.8s and auto-fails over to local Ollama.", score: 0.88, category: "ARCHITECTURE" },
];

const JarvisContext = createContext<JarvisContextType | undefined>(undefined);

export const JarvisProvider = ({ children }: { children: ReactNode }) => {
  const [persona, setPersonaState] = useState<Persona>("alfred");
  const [aiState, setAiState] = useState<AIState>("IDLE");
  const [isHandshaking, setIsHandshaking] = useState(false);
  const [meshNodes] = useState<MeshNode[]>(INITIAL_NODES);
  const [intelFeed] = useState<IntelItem[]>(INITIAL_INTEL);
  const [threatPings] = useState<ThreatPing[]>(THREAT_PINGS);
  const [messages, setMessages] = useState<DialogueMessage[]>(INITIAL_MESSAGES);
  const [vectorChunks] = useState<VectorChunk[]>(INITIAL_VECTORS);
  const [activeCommand, setActiveCommand] = useState("");
  const [worldMonitorActive, setWorldMonitorActive] = useState(false);
  const [audioWaveforms, setAudioWaveforms] = useState<number[]>(Array(32).fill(0.1));

  // Sync Persona with data-attribute on document root
  useEffect(() => {
    document.documentElement.setAttribute("data-persona", persona);
  }, [persona]);

  // Audio Engine: Pure Math.sin() simulated waveform frequencies
  useEffect(() => {
    let frame = 0;
    const interval = setInterval(() => {
      frame += 0.15;
      const waveCount = 32;
      const newWaves: number[] = [];

      let amplitudeMultiplier = 0.15; // IDLE
      if (aiState === "LISTENING") amplitudeMultiplier = 0.75;
      if (aiState === "THINKING") amplitudeMultiplier = 0.5;
      if (aiState === "EXECUTING") amplitudeMultiplier = 0.9;
      if (aiState === "WORLD_MONITOR_ACTIVE") amplitudeMultiplier = 0.35;

      for (let i = 0; i < waveCount; i++) {
        const val =
          Math.abs(
            Math.sin(frame + i * 0.3) * 0.6 +
              Math.sin(frame * 1.5 + i * 0.7) * 0.4
          ) * amplitudeMultiplier;
        newWaves.push(Math.max(0.06, Math.min(1.0, val)));
      }
      setAudioWaveforms(newWaves);
    }, 45);

    return () => clearInterval(interval);
  }, [aiState]);

  // Persona switching with 1.2s handshake glitch transition
  const setPersona = (newPersona: Persona) => {
    if (newPersona === persona || isHandshaking) return;
    setIsHandshaking(true);
    setTimeout(() => {
      setPersonaState(newPersona);
      setTimeout(() => {
        setIsHandshaking(false);
      }, 600);
    }, 600);
  };

  const togglePersona = () => {
    setPersona(persona === "ev" ? "alfred" : "ev");
  };

  const toggleWorldMonitor = () => {
    if (aiState === "WORLD_MONITOR_ACTIVE") {
      setAiState("IDLE");
      setWorldMonitorActive(false);
    } else {
      setAiState("WORLD_MONITOR_ACTIVE");
      setWorldMonitorActive(true);
    }
  };

  const triggerAudioPing = () => {
    setAiState("LISTENING");
    setTimeout(() => {
      setAiState("THINKING");
      setTimeout(() => {
        setAiState("EXECUTING");
        setTimeout(() => {
          setAiState("IDLE");
        }, 1200);
      }, 1500);
    }, 1200);
  };

  const submitCommand = async (cmd: string) => {
    if (!cmd.trim()) return;
    setActiveCommand(cmd);

    const userMsg: DialogueMessage = {
      id: `msg-user-${Date.now()}`,
      sender: "user",
      text: cmd,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    // Step 1: Listening
    setAiState("LISTENING");
    await new Promise((r) => setTimeout(r, 600));

    // Step 2: Thinking & Routing
    setAiState("THINKING");
    const isCode = /code|python|script|debug|function|build|make/i.test(cmd);
    const isMath = /solve|calculate|derivative|proof|math|deep/i.test(cmd);
    const targetNode = isMath ? "Worker 3 (RTX 5050)" : isCode ? "Worker 1 (RTX 4050)" : "NANI Master";
    const targetModel = isMath ? "deepseek-r1:14b" : isCode ? "qwen2.5-coder:7b" : "jarvis:latest";

    await new Promise((r) => setTimeout(r, 1200));

    // Step 3: Executing
    setAiState("EXECUTING");
    await new Promise((r) => setTimeout(r, 1000));

    const responseText = isMath
      ? `Calculated using deep multi-step mathematical reasoning on ${targetNode}. All boundary conditions confirmed.`
      : isCode
      ? `Generated modular implementation via ${targetModel} on ${targetNode}. Architecture verified with zero syntax errors.`
      : `Acknowledged, Charan. Executed intent across ${targetNode} with RAG grounding from 2,736 memory vectors.`;

    const jarvisMsg: DialogueMessage = {
      id: `msg-jarvis-${Date.now()}`,
      sender: "jarvis",
      text: responseText,
      thought: `1. Analyzed user intent: "${cmd}"\n2. Classified task -> Routed to ${targetNode} (${targetModel})\n3. Injected semantic context from ChromaDB\n4. Verified tool safety and execution.`,
      timestamp: new Date().toLocaleTimeString(),
      nodeUsed: targetNode,
      modelUsed: targetModel,
      latency: +(Math.random() * 0.4 + 0.1).toFixed(2),
    };

    setMessages((prev) => [...prev, jarvisMsg]);
    setAiState("IDLE");
  };

  return (
    <JarvisContext.Provider
      value={{
        persona,
        setPersona,
        togglePersona,
        aiState,
        setAiState,
        isHandshaking,
        audioWaveforms,
        meshNodes,
        intelFeed,
        threatPings,
        messages,
        vectorChunks,
        totalVectors: 2736,
        activeCommand,
        submitCommand,
        triggerAudioPing,
        worldMonitorActive,
        toggleWorldMonitor,
      }}
    >
      {children}
    </JarvisContext.Provider>
  );
};

export const useJarvis = () => {
  const context = useContext(JarvisContext);
  if (!context) {
    throw new Error("useJarvis must be used within a JarvisProvider");
  }
  return context;
};
