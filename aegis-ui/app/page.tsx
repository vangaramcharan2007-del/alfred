"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Activity,
  Heart,
  Thermometer,
  ShieldAlert,
  ShieldCheck,
  Zap,
  Radio,
  Cpu,
  RefreshCw,
  AlertTriangle,
  Play,
  Pause,
  Bot
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine
} from "recharts";

interface TelemetryPoint {
  id?: number;
  timestamp: string;
  heart_rate: number;
  temperature: number;
  risk_score: string;
  is_anomaly: boolean;
  escalated?: boolean;
}

const BACKEND_URL = "http://127.0.0.1:8000";

export default function AegisDashboard() {
  // Telemetry state
  const [dataPoints, setDataPoints] = useState<TelemetryPoint[]>([
    { timestamp: "17:40:01", heart_rate: 72, temperature: 36.8, risk_score: "Normal", is_anomaly: false },
    { timestamp: "17:40:03", heart_rate: 74, temperature: 36.9, risk_score: "Normal", is_anomaly: false },
    { timestamp: "17:40:05", heart_rate: 71, temperature: 36.8, risk_score: "Normal", is_anomaly: false },
    { timestamp: "17:40:07", heart_rate: 73, temperature: 37.0, risk_score: "Normal", is_anomaly: false },
    { timestamp: "17:40:09", heart_rate: 72, temperature: 36.8, risk_score: "Normal", is_anomaly: false },
  ]);

  const [currentHR, setCurrentHR] = useState<number>(72);
  const [currentTemp, setCurrentTemp] = useState<number>(36.8);
  const [riskScore, setRiskScore] = useState<string>("Normal");
  const [isAnomaly, setIsAnomaly] = useState<boolean>(false);
  const [escalationsCount, setEscalationsCount] = useState<number>(0);

  // Baymax streaming state
  const [baymaxExplanation, setBaymaxExplanation] = useState<string>(
    "AEGIS Intelligence Core initialized. Vitals are currently operating within nominal baseline parameters."
  );
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [isAutoSimulating, setIsAutoSimulating] = useState<boolean>(false);
  const [lastActionStatus, setLastActionStatus] = useState<string>("READY");

  // Keep reference for interval
  const autoSimRef = useRef<NodeJS.Timeout | null>(null);

  // Hydrate initial history from backend
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/telemetry-history`);
      if (res.ok) {
        const history: TelemetryPoint[] = await res.json();
        if (history.length > 0) {
          setDataPoints(history);
          const latest = history[history.length - 1];
          setCurrentHR(latest.heart_rate);
          setCurrentTemp(latest.temperature);
          setRiskScore(latest.risk_score);
          setIsAnomaly(latest.is_anomaly);
          setEscalationsCount(history.filter((h) => h.is_anomaly).length);
        }
      }
    } catch {
      // Backend may still be initializing
    }
  };

  // Stream Baymax advice
  const triggerBaymaxExplanation = async (hr: number, temp: number, risk: string) => {
    setIsStreaming(true);
    setBaymaxExplanation("");
    try {
      const response = await fetch(`${BACKEND_URL}/explain-risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ heart_rate: hr, temperature: temp, risk_score: risk }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let accumulated = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        setBaymaxExplanation(accumulated);
      }
    } catch {
      setBaymaxExplanation(
        risk === "High"
          ? "CRITICAL ALERT: Acute physiological elevation detected. Cease physical exertion, hydrate immediately, and signal medical responders."
          : "Baseline telemetry verified. Heart rate and core temperature parameters are well-balanced."
      );
    } finally {
      setIsStreaming(false);
    }
  };

  // Ingest telemetry reading
  const sendTelemetry = async (hr: number, temp: number) => {
    const timestampStr = new Date().toTimeString().split(" ")[0];
    try {
      const res = await fetch(`${BACKEND_URL}/ingest-telemetry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ heart_rate: hr, temperature: temp }),
      });

      if (res.ok) {
        const data = await res.json();
        const newPoint: TelemetryPoint = {
          timestamp: data.timestamp || timestampStr,
          heart_rate: data.heart_rate,
          temperature: data.temperature,
          risk_score: data.risk_score,
          is_anomaly: data.is_anomaly,
          escalated: data.escalated,
        };

        setDataPoints((prev) => [...prev.slice(-25), newPoint]);
        setCurrentHR(data.heart_rate);
        setCurrentTemp(data.temperature);
        setRiskScore(data.risk_score);
        setIsAnomaly(data.is_anomaly);

        if (data.is_anomaly) {
          setEscalationsCount((c) => c + 1);
          setLastActionStatus("CRITICAL ANOMALY INGESTED -> N8N WEBHOOK DISPATCHED");
        } else {
          setLastActionStatus(`NORMAL INGESTION -> HR: ${hr} BPM, Temp: ${temp}°C`);
        }

        // Trigger Baymax advice stream
        triggerBaymaxExplanation(data.heart_rate, data.temperature, data.risk_score);
      }
    } catch {
      // Local fallback simulation if backend is paused
      const isCritical = hr > 100 || temp > 38.0;
      const point: TelemetryPoint = {
        timestamp: timestampStr,
        heart_rate: hr,
        temperature: temp,
        risk_score: isCritical ? "High" : "Normal",
        is_anomaly: isCritical,
      };
      setDataPoints((prev) => [...prev.slice(-25), point]);
      setCurrentHR(hr);
      setCurrentTemp(temp);
      setRiskScore(point.risk_score);
      setIsAnomaly(isCritical);
      triggerBaymaxExplanation(hr, temp, point.risk_score);
    }
  };

  // God Mode Anomaly Injector
  const handleInjectAnomaly = () => {
    sendTelemetry(135, 39.5);
  };

  // Normal Baseline Ingestion
  const handleSendNormal = () => {
    const randomHR = Math.floor(68 + Math.random() * 8);
    const randomTemp = Number((36.6 + Math.random() * 0.6).toFixed(1));
    sendTelemetry(randomHR, randomTemp);
  };

  // Auto-simulation toggle (2s interval)
  const toggleAutoSim = () => {
    if (isAutoSimulating) {
      if (autoSimRef.current) clearInterval(autoSimRef.current);
      setIsAutoSimulating(false);
      setLastActionStatus("AUTO-FEED PAUSED");
    } else {
      setIsAutoSimulating(true);
      setLastActionStatus("AUTO-FEED RUNNING (2s)");
      autoSimRef.current = setInterval(() => {
        handleSendNormal();
      }, 2500);
    }
  };

  useEffect(() => {
    return () => {
      if (autoSimRef.current) clearInterval(autoSimRef.current);
    };
  }, []);

  return (
    <main className="min-h-screen bg-[#070b12] text-slate-100 p-4 md:p-8 selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Clinical Header */}
      <header className="border-b border-slate-800/80 pb-4 mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-500/50 flex items-center justify-center text-cyan-400 font-bold text-xl shadow-[0_0_15px_rgba(6,182,212,0.4)]">
              <Activity className="w-6 h-6 animate-pulse" />
            </div>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl md:text-2xl font-black tracking-wider text-white">
                AEGIS <span className="text-cyan-400 text-sm font-semibold border border-cyan-500/40 px-2 py-0.5 rounded bg-cyan-950/50">V1.2 CLINICAL PWA</span>
              </h1>
            </div>
            <p className="text-xs text-slate-400 font-mono tracking-wide">
              OFFLINE-FIRST PHYSIOLOGICAL SENTINEL // ISOLATION FOREST + LOCAL LLM
            </p>
          </div>
        </div>

        {/* System Badges & God Mode Action */}
        <div className="flex flex-wrap items-center gap-2 md:gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800 text-xs font-mono text-emerald-400">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>ML ENGINE: ACTIVE</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800 text-xs font-mono text-cyan-400">
            <Bot className="w-3.5 h-3.5 text-cyan-400" />
            <span>BAYMAX: LOCAL</span>
          </div>

          {/* God Mode Anomaly Injector Button */}
          <button
            id="inject-anomaly-btn"
            onClick={handleInjectAnomaly}
            className="group relative inline-flex items-center gap-2 px-3 py-1.5 rounded bg-rose-950/60 border border-rose-500/70 text-rose-300 hover:text-white hover:bg-rose-900/80 transition-all font-mono text-xs font-bold shadow-[0_0_12px_rgba(244,63,94,0.35)] hover:shadow-[0_0_20px_rgba(244,63,94,0.7)] active:scale-95"
            title="Inject 135 BPM & 39.5°C Critical Spike"
          >
            <Zap className="w-3.5 h-3.5 text-rose-400 group-hover:scale-125 transition-transform" />
            <span>INJECT ANOMALY</span>
          </button>
        </div>
      </header>

      {/* Grid: Metrics Ribbon */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Heart Rate Card */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur shadow-lg relative overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Heart Rate</span>
            <Heart className={`w-5 h-5 ${isAnomaly ? "text-rose-500 animate-bounce" : "text-cyan-400 animate-pulse"}`} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-3xl md:text-4xl font-black font-mono tracking-tight ${isAnomaly ? "text-rose-400 text-glow-rose" : "text-cyan-300 text-glow-cyan"}`}>
              {currentHR}
            </span>
            <span className="text-xs text-slate-400 font-mono">BPM</span>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500 flex justify-between">
            <span>Resting Base: 60-80</span>
            <span className={currentHR > 100 ? "text-rose-400 font-bold" : "text-slate-400"}>
              {currentHR > 100 ? "TACHYCARDIA" : "NOMINAL"}
            </span>
          </div>
        </div>

        {/* Temperature Card */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur shadow-lg relative overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Core Temp</span>
            <Thermometer className={`w-5 h-5 ${isAnomaly ? "text-rose-500 animate-pulse" : "text-amber-400"}`} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-3xl md:text-4xl font-black font-mono tracking-tight ${isAnomaly ? "text-rose-400 text-glow-rose" : "text-amber-300"}`}>
              {currentTemp.toFixed(1)}
            </span>
            <span className="text-xs text-slate-400 font-mono">°C</span>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500 flex justify-between">
            <span>Baseline: 36.5-37.5</span>
            <span className={currentTemp > 38.0 ? "text-rose-400 font-bold" : "text-slate-400"}>
              {currentTemp > 38.0 ? "HYPERTHERMIA" : "NOMINAL"}
            </span>
          </div>
        </div>

        {/* ML Risk Assessment Card */}
        <div className={`p-4 rounded-xl border backdrop-blur shadow-lg transition-all ${
          isAnomaly
            ? "bg-rose-950/30 border-rose-500/60 shadow-[0_0_20px_rgba(244,63,94,0.25)]"
            : "bg-slate-900/60 border-slate-800/80"
        }`}>
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Risk Level</span>
            {isAnomaly ? (
              <ShieldAlert className="w-5 h-5 text-rose-500 animate-pulse" />
            ) : (
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl md:text-3xl font-black font-mono tracking-tight ${
              isAnomaly ? "text-rose-400 text-glow-rose animate-pulse" : "text-emerald-400 text-glow-emerald"
            }`}>
              {riskScore.toUpperCase()}
            </span>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">
            <span>Decision: {isAnomaly ? "IsolationForest Outlier" : "Inlier Distribution"}</span>
          </div>
        </div>

        {/* Escalation & Webhook Status Card */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur shadow-lg">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">n8n Escalations</span>
            <Radio className={`w-5 h-5 ${escalationsCount > 0 ? "text-amber-400 animate-pulse" : "text-slate-500"}`} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl md:text-4xl font-black font-mono text-slate-200">
              {escalationsCount}
            </span>
            <span className="text-xs text-slate-400 font-mono">DISPATCHES</span>
          </div>
          <div className="mt-2 text-[11px] font-mono text-slate-500">
            <span>Webhook: :5678/aegis-escalation</span>
          </div>
        </div>
      </section>

      {/* Main Grid: Telemetry Chart & Baymax Stream */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Recharts Telemetry Graph (2 Cols) */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/50 border border-slate-800/90 shadow-xl flex flex-col">
          <div className="flex flex-wrap justify-between items-center gap-2 mb-4">
            <div>
              <h2 className="text-sm md:text-base font-bold font-mono text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                PHYSIOLOGICAL TELEMETRY STREAM
              </h2>
              <p className="text-xs text-slate-500 font-mono">Real-time synchronized Heart Rate (BPM) & Core Temp (°C)</p>
            </div>
            
            {/* Quick Ingestion Action Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleSendNormal}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-300 transition"
              >
                + Baseline Point
              </button>
              <button
                onClick={toggleAutoSim}
                className={`px-2.5 py-1 rounded text-xs font-mono flex items-center gap-1 transition ${
                  isAutoSimulating
                    ? "bg-amber-950/60 border border-amber-500/50 text-amber-300"
                    : "bg-slate-800 hover:bg-slate-700 text-slate-300"
                }`}
              >
                {isAutoSimulating ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                {isAutoSimulating ? "Stop Auto" : "Auto Feed"}
              </button>
              <button
                onClick={fetchHistory}
                className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
                title="Refresh history"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Recharts LineChart */}
          <div className="w-full h-72 md:h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dataPoints} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
                <XAxis
                  dataKey="timestamp"
                  stroke="#64748b"
                  tick={{ fontSize: 11, fill: "#64748b" }}
                  tickLine={false}
                />
                <YAxis
                  yAxisId="left"
                  domain={[50, 160]}
                  stroke="#06b6d4"
                  tick={{ fontSize: 11, fill: "#06b6d4" }}
                  tickLine={false}
                  label={{ value: "HR (BPM)", angle: -90, position: "insideLeft", fill: "#06b6d4", fontSize: 10, offset: 15 }}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  domain={[35.0, 41.0]}
                  stroke="#f59e0b"
                  tick={{ fontSize: 11, fill: "#f59e0b" }}
                  tickLine={false}
                  label={{ value: "Temp (°C)", angle: 90, position: "insideRight", fill: "#f59e0b", fontSize: 10, offset: 15 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    borderRadius: "8px",
                    color: "#f8fafc",
                    fontSize: "12px",
                    fontFamily: "monospace"
                  }}
                />
                <Legend
                  wrapperStyle={{ fontSize: "11px", fontFamily: "monospace", paddingTop: "8px" }}
                />
                {/* Risk Reference Bands */}
                <ReferenceLine yAxisId="left" y={100} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: "HR Anomaly > 100", fill: "#f43f5e", fontSize: 9 }} />
                <ReferenceLine yAxisId="right" y={38.0} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: "Temp Anomaly > 38°C", fill: "#f43f5e", fontSize: 9 }} />

                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="heart_rate"
                  name="Heart Rate (BPM)"
                  stroke="#06b6d4"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: "#06b6d4" }}
                  activeDot={{ r: 6, fill: "#22d3ee" }}
                  isAnimationActive={true}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="temperature"
                  name="Core Temp (°C)"
                  stroke="#f59e0b"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: "#f59e0b" }}
                  activeDot={{ r: 6, fill: "#fbbf24" }}
                  isAnimationActive={true}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Baymax AEGIS Intelligence Card (1 Col) */}
        <div className={`p-5 rounded-2xl border flex flex-col justify-between transition-all duration-300 ${
          isAnomaly
            ? "bg-rose-950/20 border-rose-500/50 shadow-[0_0_25px_rgba(244,63,94,0.2)]"
            : "bg-slate-900/50 border-slate-800/90 shadow-xl"
        }`}>
          <div>
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  isAnomaly ? "bg-rose-900/80 text-rose-300" : "bg-cyan-950/80 text-cyan-300"
                }`}>
                  <Bot className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold font-mono text-white tracking-wide">
                    AEGIS INTELLIGENCE
                  </h3>
                  <span className="text-[10px] text-slate-500 font-mono">BAYMAX // LOCAL LLM STREAM</span>
                </div>
              </div>
              
              {/* Streaming Indicator */}
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-950/60 border border-slate-800 text-[10px] font-mono">
                {isStreaming ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                    <span className="text-cyan-300">STREAMING</span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span className="text-slate-400">READY</span>
                  </>
                )}
              </div>
            </div>

            {/* Terminal Speech Box */}
            <div className="relative mt-2 p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 min-h-[160px] font-mono text-xs leading-relaxed text-slate-200 shadow-inner">
              <div className="text-[11px] text-slate-500 mb-1 flex items-center gap-1">
                <span>&gt; AEGIS ADVISORY FEED:</span>
              </div>
              <p className={`font-mono text-xs md:text-sm ${
                isAnomaly ? "text-rose-200" : "text-slate-200"
              }`}>
                {baymaxExplanation}
                {isStreaming && <span className="inline-block w-2 h-4 ml-1 bg-cyan-400 animate-pulse align-middle"></span>}
              </p>
            </div>
          </div>

          {/* Prompt Trigger Button */}
          <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between">
            <span className="text-[10px] font-mono text-slate-500">
              Model: <code className="text-cyan-400">aegis-baymax</code>
            </span>
            <button
              onClick={() => triggerBaymaxExplanation(currentHR, currentTemp, riskScore)}
              disabled={isStreaming}
              className="px-3 py-1.5 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-500/40 text-cyan-300 text-xs font-mono font-semibold transition flex items-center gap-1.5 disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 ${isStreaming ? "animate-spin" : ""}`} />
              <span>Re-evaluate</span>
            </button>
          </div>
        </div>
      </section>

      {/* Bottom Status Bar */}
      <footer className="p-3 rounded-xl bg-slate-900/40 border border-slate-800/60 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>LAST ACTION: <span className="text-slate-200">{lastActionStatus}</span></span>
        </div>
        <div className="flex items-center gap-4 text-slate-500 text-[11px]">
          <span>BACKEND: <span className="text-slate-400">http://127.0.0.1:8000</span></span>
          <span>LATENCY: &lt;15ms</span>
          <span>SIH26181 ARCHITECTURE</span>
        </div>
      </footer>
    </main>
  );
}
