export type Persona = "ev" | "alfred";

export type AIState = "IDLE" | "LISTENING" | "THINKING" | "EXECUTING" | "WORLD_MONITOR_ACTIVE";

export interface MeshNode {
  id: string;
  name: string;
  role: string;
  hardware: string;
  ip: string;
  status: "online" | "offline" | "busy" | "pending";
  vram: string;
  models: string[];
  latencyMs: number;
  loadPercent: number;
}

export interface IntelItem {
  id: string;
  timestamp: string;
  category: "INTEL" | "SECURITY" | "MESH" | "CLUSTER" | "SATELLITE";
  severity: "INFO" | "WARN" | "CRITICAL";
  title: string;
  source: string;
  coordinates?: [number, number];
}

export interface ThreatPing {
  id: string;
  name: string;
  lat: number;
  lng: number;
  threatLevel: "ELEVATED" | "HIGH" | "CRITICAL";
  vector: string;
  status: string;
}

export interface DialogueMessage {
  id: string;
  sender: "user" | "jarvis";
  text: string;
  thought?: string;
  timestamp: string;
  nodeUsed?: string;
  modelUsed?: string;
  latency?: number;
}

export interface VectorChunk {
  id: string;
  source: string;
  content: string;
  score: number;
  category: string;
}
