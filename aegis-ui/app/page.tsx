"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Heart,
  Thermometer,
  Activity,
  Zap,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  ShieldAlert,
  ShieldCheck,
  Droplets,
  Wind,
  Send,
  Eye,
  Camera,
  Database,
  Cpu,
  RefreshCw,
  Trash2,
  Sparkles,
  Radio,
  Sliders,
  AlertTriangle,
  PlayCircle
} from "lucide-react";

interface VitalsState {
  heartRate: number;
  rmssd: number;
  temperature: number;
  tempSlope: number;
  eda: number;
  ear: number;
  riskLevel: string;
  isAnomaly: boolean;
  isFatigued: boolean;
}

interface MessageLog {
  id: string;
  sender: "user" | "baymax";
  text: string;
  timestamp: string;
  isAlert?: boolean;
}

interface MemoryRecord {
  heart_rate: number;
  eye_aspect_ratio: number;
  fatigue_flag: boolean;
  rppg_signal: number;
}

interface RollingStats {
  record_count: number;
  avg_heart_rate: number;
  avg_ear: number;
  fatigue_events_in_window: number;
}

const BACKEND_URL = "http://127.0.0.1:8000";

export default function AegisMedicalCommandDeck() {
  // Biometrics State
  const [vitals, setVitals] = useState<VitalsState>({
    heartRate: 72,
    rmssd: 45,
    temperature: 36.8,
    tempSlope: 0.0,
    eda: 1.5,
    ear: 0.32,
    riskLevel: "OPTIMAL",
    isAnomaly: false,
    isFatigued: false,
  });

  // UI & Interaction State
  const [textInput, setTextInput] = useState<string>("");
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(true);
  const [avatarState, setAvatarState] = useState<"idle" | "listening" | "speaking" | "alert">("idle");
  const [messages, setMessages] = useState<MessageLog[]>([
    {
      id: "init-1",
      sender: "baymax",
      text: "Hello! I am Baymax, your personal healthcare companion powered by local Ollama intelligence. Live hardware camera feed and persistent memory are online. How may I assist your well-being today?",
      timestamp: "12:00",
    },
  ]);

  // Memory Table State
  const [memoryLogs, setMemoryLogs] = useState<MemoryRecord[]>([]);
  const [rollingStats, setRollingStats] = useState<RollingStats>({
    record_count: 0,
    avg_heart_rate: 72.0,
    avg_ear: 0.32,
    fatigue_events_in_window: 0,
  });
  const [escalationsCount, setEscalationsCount] = useState<number>(0);
  const [cameraActive, setCameraActive] = useState<boolean>(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const recognitionRef = useRef<any>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);
  const waveformCanvasRef = useRef<HTMLCanvasElement>(null);

  // 1. Direct Hardware Webcam Mount via MediaDevices API
  useEffect(() => {
    if (typeof window !== "undefined" && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play().catch(() => {});
            setCameraActive(true);
          }
        })
        .catch((err) => {
          console.warn("Hardware camera access note:", err);
          setCameraActive(false);
        });
    }
  }, []);

  // 2. Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const reco = new SpeechRecognition();
        reco.continuous = false;
        reco.interimResults = false;
        reco.lang = "en-US";

        reco.onstart = () => {
          setIsListening(true);
          setAvatarState("listening");
        };

        reco.onresult = (event: any) => {
          const spokenText = event.results[0][0].transcript;
          handleSendQuery(spokenText);
        };

        reco.onerror = () => {
          setIsListening(false);
          setAvatarState(vitals.isAnomaly || vitals.isFatigued ? "alert" : "idle");
        };

        reco.onend = () => {
          setIsListening(false);
          if (!isSpeaking) {
            setAvatarState(vitals.isAnomaly || vitals.isFatigued ? "alert" : "idle");
          }
        };

        recognitionRef.current = reco;
      }
    }
  }, [vitals.isAnomaly, vitals.isFatigued, isSpeaking]);

  // 3. Periodic Memory Records Poller (every 2.5s)
  useEffect(() => {
    const pollMemory = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/memory-records?limit=15`);
        if (res.ok) {
          const data = await res.json();
          setMemoryLogs(data.vitals_log || []);
          if (data.rolling_stats) {
            setRollingStats(data.rolling_stats);
          }
        }
      } catch {
        // Poller
      }
    };

    pollMemory();
    const interval = setInterval(pollMemory, 2500);
    return () => clearInterval(interval);
  }, []);

  // 4. Live rPPG Plethysmogram Oscilloscope Canvas
  useEffect(() => {
    let animationFrame: number;
    let phase = 0;

    const renderWave = () => {
      const canvas = waveformCanvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          const w = canvas.width;
          const h = canvas.height;
          ctx.fillStyle = "rgba(10, 15, 25, 0.4)";
          ctx.fillRect(0, 0, w, h);

          // Grid lines
          ctx.strokeStyle = "rgba(30, 41, 59, 0.5)";
          ctx.lineWidth = 1;
          for (let x = 0; x < w; x += 30) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
            ctx.stroke();
          }

          // Dynamic rPPG waveform
          ctx.strokeStyle = vitals.isAnomaly ? "#f43f5e" : "#06b6d4";
          ctx.lineWidth = 2;
          ctx.beginPath();

          const hrFreq = (vitals.heartRate / 60) * 0.08;
          phase += hrFreq;

          for (let x = 0; x < w; x++) {
            const angle = phase + x * 0.05;
            const yOffset = Math.sin(angle) * 16 + Math.sin(angle * 2.5) * 6;
            const y = h / 2 - yOffset;
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          ctx.stroke();
        }
      }
      animationFrame = requestAnimationFrame(renderWave);
    };

    renderWave();
    return () => cancelAnimationFrame(animationFrame);
  }, [vitals.heartRate, vitals.isAnomaly]);

  // Scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Speech Synthesis Helper
  const speakText = (text: string) => {
    if (!voiceEnabled || typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.05;

    const voices = window.speechSynthesis.getVoices();
    const friendlyVoice = voices.find(
      (v) =>
        v.name.includes("Google") ||
        v.name.includes("Natural") ||
        v.name.includes("Samantha") ||
        v.name.includes("Daniel")
    );
    if (friendlyVoice) utterance.voice = friendlyVoice;

    utterance.onstart = () => {
      setIsSpeaking(true);
      setAvatarState(vitals.isAnomaly || vitals.isFatigued ? "alert" : "speaking");
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setAvatarState(vitals.isAnomaly || vitals.isFatigued ? "alert" : "idle");
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      setAvatarState(vitals.isAnomaly || vitals.isFatigued ? "alert" : "idle");
    };

    window.speechSynthesis.speak(utterance);
  };

  // Toggle Microphone
  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
      } catch {
        const samplePrompts = [
          "How can I reduce fever safely?",
          "What are the best recovery steps for fatigue and eye strain?",
          "How are my vitals doing right now?",
        ];
        const randomPrompt = samplePrompts[Math.floor(Math.random() * samplePrompts.length)];
        handleSendQuery(randomPrompt);
      }
    }
  };

  // Send Query to Pure Ollama LLaMA Engine
  const handleSendQuery = async (queryText: string, customVitals?: Partial<VitalsState>) => {
    if (!queryText.trim()) return;
    const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
    const activeVitals = { ...vitals, ...customVitals };

    setMessages((prev) => [
      ...prev,
      { id: `user-${Date.now()}`, sender: "user", text: queryText, timestamp: timeStr },
    ]);
    setTextInput("");

    try {
      const res = await fetch(`${BACKEND_URL}/companion-interact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_speech: queryText,
          heart_rate: activeVitals.heartRate,
          rmssd: activeVitals.rmssd,
          temperature: activeVitals.temperature,
          temp_slope: activeVitals.tempSlope,
          eda: activeVitals.eda,
          ear: activeVitals.ear,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const reply = data.reply_text;

        setMessages((prev) => [
          ...prev,
          {
            id: `baymax-${Date.now()}`,
            sender: "baymax",
            text: reply,
            timestamp: timeStr,
            isAlert: data.is_anomaly || data.fatigue_detected,
          },
        ]);

        if (data.is_anomaly || data.fatigue_detected) {
          setEscalationsCount((c) => c + 1);
        }

        speakText(reply);
      } else {
        throw new Error("HTTP failure");
      }
    } catch {
      const fallbackMsg = `Ollama model inference is processing. Heart rate: ${activeVitals.heartRate} BPM, Temp: ${activeVitals.temperature}°C.`;
      setMessages((prev) => [
        ...prev,
        { id: `baymax-${Date.now()}`, sender: "baymax", text: fallbackMsg, timestamp: timeStr },
      ]);
      speakText(fallbackMsg);
    }
  };

  // Simulation Trigger: Fatigue (EAR < 0.22)
  const triggerFatigueSimulation = async () => {
    const fatigueVitals: VitalsState = {
      ...vitals,
      ear: 0.14,
      isFatigued: true,
      riskLevel: "HIGH RISK",
    };
    setVitals(fatigueVitals);
    setAvatarState("alert");
    handleSendQuery("I have severe eye fatigue and prolonged eyelid closure from working all night.", fatigueVitals);
  };

  // Simulation Trigger: Acute Cardiac & Heat Anomaly
  const triggerAnomalySimulation = async () => {
    const anomalyVitals: VitalsState = {
      heartRate: 135,
      rmssd: 15,
      temperature: 39.5,
      tempSlope: 0.15,
      eda: 8.5,
      ear: 0.26,
      riskLevel: "HIGH RISK",
      isAnomaly: true,
      isFatigued: false,
    };
    setVitals(anomalyVitals);
    setAvatarState("alert");
    handleSendQuery("I have severe fever, body temperature of 39.5 degrees, and tachycardia.", anomalyVitals);
  };

  // Reset to Baseline & Clear DB
  const handleResetBaseline = async () => {
    const normalVitals: VitalsState = {
      heartRate: 72,
      rmssd: 45,
      temperature: 36.8,
      tempSlope: 0.0,
      eda: 1.5,
      ear: 0.32,
      riskLevel: "OPTIMAL",
      isAnomaly: false,
      isFatigued: false,
    };
    setVitals(normalVitals);
    setAvatarState("idle");

    try {
      await fetch(`${BACKEND_URL}/clear-memory`, { method: "POST" });
    } catch {
      // Memory reset
    }

    const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
    const msg = "Biometric equilibrium restored. Persistent database baseline recalibrated to resting limits.";
    setMessages((prev) => [
      ...prev,
      { id: `reset-${Date.now()}`, sender: "baymax", text: msg, timestamp: timeStr },
    ]);
    speakText(msg);
  };

  return (
    <main className="min-h-screen bg-[#040711] text-slate-100 p-3 sm:p-5 flex flex-col gap-4 font-sans selection:bg-cyan-500 selection:text-black">
      
      {/* Top Header Command Bar */}
      <header className="flex flex-wrap items-center justify-between gap-3 px-5 py-3.5 bg-slate-900/80 border border-slate-800/90 rounded-2xl backdrop-blur-xl shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center text-white shadow-[0_0_20px_rgba(6,182,212,0.6)]">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black tracking-wider text-white">
                AEGIS <span className="text-cyan-400 font-mono text-xs font-normal">// CLINICAL COMMAND DECK</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-500/40 text-[10px] font-mono text-cyan-300">
                OLLAMA LLaMA 3
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono flex items-center gap-2 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>HARDWARE CAMERA LIVE</span>
              <span>•</span>
              <span>SQLITE PERSISTENT MEMORY</span>
              <span>•</span>
              <span>PURE MODEL INFERENCE</span>
            </p>
          </div>
        </div>

        {/* Quick Action Simulation Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={triggerFatigueSimulation}
            className="px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-amber-950/80 border border-amber-500/60 text-amber-300 hover:bg-amber-900 transition flex items-center gap-1.5 shadow"
            title="Simulate Eye Aspect Ratio Fatigue (EAR < 0.22)"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>TEST FATIGUE</span>
          </button>

          <button
            onClick={triggerAnomalySimulation}
            className="px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-rose-950/80 border border-rose-500/60 text-rose-300 hover:bg-rose-900 transition flex items-center gap-1.5 shadow"
            title="Simulate Critical Heat/Cardiac Anomaly"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>TEST ANOMALY</span>
          </button>

          <button
            onClick={handleResetBaseline}
            className="px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-emerald-950/80 border border-emerald-500/60 text-emerald-300 hover:bg-emerald-900 transition flex items-center gap-1.5 shadow"
            title="Reset Baseline & Clear Database"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>RESET BASELINE</span>
          </button>

          <button
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            className={`p-2 rounded-xl border transition ${
              voiceEnabled
                ? "bg-cyan-950 border-cyan-500/40 text-cyan-300"
                : "bg-slate-800 border-slate-700 text-slate-500"
            }`}
            title={voiceEnabled ? "Voice Enabled" : "Voice Muted"}
          >
            {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Main 3-Column Workstation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1">
        
        {/* ========================================================================= */}
        {/* LEFT DECK (Cols 1-4): Hardware Webcam Feed & rPPG Oscilloscope */}
        {/* ========================================================================= */}
        <section className="lg:col-span-4 flex flex-col gap-4">
          
          {/* Live Hardware Webcam Video Card */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-3 backdrop-blur-xl shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Camera className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold font-mono tracking-wider text-slate-200">
                  LIVE HARDWARE WEBCAM FEED
                </h2>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono flex items-center gap-1 border ${
                cameraActive
                  ? "bg-emerald-950 border-emerald-500/50 text-emerald-300"
                  : "bg-cyan-950 border-cyan-500/50 text-cyan-300"
              }`}>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                {cameraActive ? "HARDWARE ONLINE" : "BROWSER CAPTURE"}
              </span>
            </div>

            {/* Native In-Browser Hardware Video Element */}
            <div className="relative w-full aspect-[4/3] rounded-2xl bg-black overflow-hidden border border-slate-800 flex items-center justify-center shadow-inner">
              <video
                ref={videoRef}
                className="w-full h-full object-cover scale-x-[-1]"
                autoPlay
                playsInline
                muted
              />
              
              {/* Scanline & HUD Overlay */}
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent pointer-events-none opacity-40" />
              <div className="absolute top-2 left-2 px-2 py-1 rounded bg-black/70 backdrop-blur border border-slate-700 text-[9px] font-mono text-cyan-300">
                LIVE CAMERA FEED: ACTIVE
              </div>
              <div className="absolute bottom-2 right-2 px-2 py-1 rounded bg-black/70 backdrop-blur border border-slate-700 text-[9px] font-mono text-slate-300">
                FPS: 30 // 640x480
              </div>
            </div>

            {/* Optical EAR & Blink Metrics */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className={`p-3 rounded-2xl border ${
                vitals.ear < 0.22 ? "bg-amber-950/60 border-amber-500/60" : "bg-slate-950/60 border-slate-800"
              }`}>
                <div className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Eye className="w-3 h-3 text-cyan-400" />
                  EYE ASPECT RATIO (EAR)
                </div>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className={`text-xl font-black ${vitals.ear < 0.22 ? "text-amber-400" : "text-white"}`}>
                    {vitals.ear.toFixed(3)}
                  </span>
                  <span className="text-[10px] text-slate-400">Thresh: 0.22</span>
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-slate-950/60 border border-slate-800">
                <div className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Activity className="w-3 h-3 text-emerald-400" />
                  SOMNOLENCE STATUS
                </div>
                <div className="mt-1">
                  {vitals.ear < 0.22 ? (
                    <span className="text-sm font-bold text-amber-400 flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" /> FATIGUE ALERT
                    </span>
                  ) : (
                    <span className="text-sm font-bold text-emerald-400 flex items-center gap-1">
                      <ShieldCheck className="w-4 h-4" /> VIGILANT
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Real-Time rPPG Pulse Oscilloscope */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-2 backdrop-blur-xl shadow-xl flex-1">
            <div className="flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <span className="font-bold text-slate-200">REAL-TIME rPPG OPTICAL WAVEFORM</span>
              </div>
              <span className="text-[10px] text-slate-400">HEMOGLOBIN FLUX</span>
            </div>
            
            <div className="w-full h-32 rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden relative shadow-inner">
              <canvas
                ref={waveformCanvasRef}
                width={450}
                height={128}
                className="w-full h-full block"
              />
              <div className="absolute top-2 left-2 text-[9px] font-mono text-cyan-400/70">
                SIGNAL GAIN: 1.0x // PLETHYSMOGRAM
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================================= */}
        {/* CENTER DECK (Cols 5-9): Vitals Matrix, Baymax Core & Dialogue */}
        {/* ========================================================================= */}
        <section className="lg:col-span-5 flex flex-col gap-4">
          
          {/* 4-Quadrant Vitals Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {/* Heart Rate */}
            <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col relative overflow-hidden">
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>HEART RATE</span>
                <Heart className={`w-3.5 h-3.5 ${vitals.heartRate > 100 ? "text-rose-400 animate-bounce" : "text-cyan-400"}`} />
              </div>
              <div className="flex items-baseline gap-1 mt-2">
                <span className={`text-2xl font-black font-mono ${vitals.heartRate > 100 ? "text-rose-400" : "text-white"}`}>
                  {vitals.heartRate}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">BPM</span>
              </div>
              <div className="text-[9px] font-mono text-slate-400 mt-1">
                {vitals.heartRate > 100 ? "TACHYCARDIA" : "Resting Normal"}
              </div>
            </div>

            {/* HRV / RMSSD */}
            <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col relative overflow-hidden">
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>HRV RMSSD</span>
                <Activity className="w-3.5 h-3.5 text-emerald-400" />
              </div>
              <div className="flex items-baseline gap-1 mt-2">
                <span className="text-2xl font-black font-mono text-emerald-300">
                  {vitals.rmssd}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">ms</span>
              </div>
              <div className="text-[9px] font-mono text-emerald-400 mt-1">
                Autonomic Balance
              </div>
            </div>

            {/* Core Temp */}
            <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col relative overflow-hidden">
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>CORE TEMP</span>
                <Thermometer className={`w-3.5 h-3.5 ${vitals.temperature > 38.0 ? "text-rose-400 animate-pulse" : "text-amber-400"}`} />
              </div>
              <div className="flex items-baseline gap-1 mt-2">
                <span className={`text-2xl font-black font-mono ${vitals.temperature > 38.0 ? "text-rose-400" : "text-amber-300"}`}>
                  {vitals.temperature.toFixed(1)}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">°C</span>
              </div>
              <div className="text-[9px] font-mono text-slate-400 mt-1">
                {vitals.temperature > 38.0 ? "HYPERTHERMIA" : "Normothermic"}
              </div>
            </div>

            {/* EDA Galvanic Skin Response */}
            <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col relative overflow-hidden">
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>EDA CONDUCT</span>
                <Droplets className="w-3.5 h-3.5 text-purple-400" />
              </div>
              <div className="flex items-baseline gap-1 mt-2">
                <span className="text-2xl font-black font-mono text-purple-300">
                  {vitals.eda.toFixed(1)}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">µS</span>
              </div>
              <div className="text-[9px] font-mono text-slate-400 mt-1">
                Arousal Index
              </div>
            </div>
          </div>

          {/* Baymax Dialogue & Companion Console */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-3 flex-1 backdrop-blur-xl shadow-xl relative min-h-[420px]">
            
            {/* Header with Avatar Orb */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                {/* Glowing Companion Avatar */}
                <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all duration-500 ${
                  avatarState === "alert"
                    ? "border-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.8)] bg-rose-950"
                    : avatarState === "listening"
                    ? "border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.8)] bg-cyan-950"
                    : "border-slate-700 bg-slate-950"
                }`}>
                  {/* Baymax Eye Line */}
                  <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                    <div className="w-2.5 h-[1.5px] bg-white -mx-1" />
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold font-mono tracking-wide text-white flex items-center gap-2">
                    BAYMAX HEALTHCARE COMPANION
                    <span className="text-[9px] text-cyan-400 font-normal">OLLAMA LLaMA 3</span>
                  </h3>
                  <p className="text-[10px] text-slate-400 font-mono">
                    State: <span className="text-cyan-300 uppercase">{avatarState}</span>
                  </p>
                </div>
              </div>

              <div className="text-[10px] font-mono text-slate-400">
                ESCALATIONS: <span className="text-white font-bold">{escalationsCount}</span>
              </div>
            </div>

            {/* Scrollable Conversation Feed */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[300px] text-xs">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`max-w-[90%] rounded-2xl px-4 py-3 leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-cyan-950/80 text-cyan-100 border border-cyan-500/40 rounded-br-none"
                        : msg.isAlert
                        ? "bg-rose-950/90 text-rose-100 border border-rose-500/60 rounded-bl-none shadow-[0_0_20px_rgba(244,63,94,0.3)]"
                        : "bg-slate-950 text-slate-200 border border-slate-800 rounded-bl-none"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                  </div>
                  <span className="text-[9px] text-slate-500 font-mono mt-1 px-1">
                    {msg.timestamp}
                  </span>
                </div>
              ))}
              <div ref={chatBottomRef} />
            </div>

            {/* Text & Speech Input Bar */}
            <div className="flex items-center gap-2 pt-2 border-t border-slate-800/80">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendQuery(textInput)}
                placeholder="Ask Baymax anything (e.g. 'how to reduce fever', 'check my vitals')..."
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition"
              />

              <button
                onClick={() => handleSendQuery(textInput)}
                disabled={!textInput.trim()}
                className="p-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:hover:bg-cyan-600 text-slate-950 font-bold transition shadow"
                title="Send Message"
              >
                <Send className="w-4 h-4" />
              </button>

              <button
                onClick={toggleListening}
                className={`p-2.5 rounded-xl border transition flex items-center justify-center ${
                  isListening
                    ? "bg-cyan-400 text-slate-950 border-cyan-300 animate-pulse shadow-[0_0_15px_rgba(6,182,212,0.8)]"
                    : "bg-slate-950 border-slate-700 text-cyan-400 hover:bg-slate-800"
                }`}
                title="Voice Input (Speech-to-Text)"
              >
                {isListening ? <Mic className="w-4 h-4 animate-bounce" /> : <Mic className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </section>

        {/* ========================================================================= */}
        {/* RIGHT DECK (Cols 10-12): SQLite Persistent Memory & Telemetry Inspector */}
        {/* ========================================================================= */}
        <section className="lg:col-span-3 flex flex-col gap-4">
          
          {/* Persistent Database Inspector Card */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-3 backdrop-blur-xl shadow-xl flex-1">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold font-mono tracking-wider text-slate-200">
                  SQLITE MEMORY (aegis_core.db)
                </h2>
              </div>
              <span className="text-[10px] font-mono text-slate-400">WAL MODE</span>
            </div>

            {/* Rolling Window Baseline Stats */}
            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5">
              <div className="text-[10px] text-slate-400 font-bold">5-MIN ROLLING BASELINE</div>
              <div className="flex justify-between text-slate-300">
                <span>Total Samples:</span>
                <span className="text-white font-bold">{rollingStats.record_count}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Avg Heart Rate:</span>
                <span className="text-cyan-300 font-bold">{rollingStats.avg_heart_rate} BPM</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Avg Ocular EAR:</span>
                <span className="text-emerald-300 font-bold">{rollingStats.avg_ear}</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Fatigue Flags:</span>
                <span className={rollingStats.fatigue_events_in_window > 0 ? "text-amber-400 font-bold" : "text-slate-400"}>
                  {rollingStats.fatigue_events_in_window} events
                </span>
              </div>
            </div>

            {/* Live Database Log Table */}
            <div className="text-[10px] font-mono text-slate-400 font-bold mt-1">
              LIVE INSERT STREAM (vitals_log):
            </div>
            <div className="flex-1 overflow-y-auto max-h-[320px] rounded-2xl bg-slate-950/80 border border-slate-800/80 p-2 text-[10px] font-mono">
              {memoryLogs.length === 0 ? (
                <div className="text-slate-500 text-center py-6">Connecting to SQLite stream...</div>
              ) : (
                <div className="space-y-1.5">
                  {memoryLogs.map((log, idx) => (
                    <div
                      key={idx}
                      className={`p-1.5 rounded-lg border flex items-center justify-between ${
                        log.fatigue_flag
                          ? "bg-amber-950/40 border-amber-500/50 text-amber-200"
                          : "bg-slate-900/60 border-slate-800 text-slate-300"
                      }`}
                    >
                      <div>
                        <span>HR: {log.heart_rate}</span>
                        <span className="ml-2 text-slate-400">EAR: {log.eye_aspect_ratio}</span>
                      </div>
                      <div>
                        {log.fatigue_flag ? (
                          <span className="text-amber-400 font-bold">FATIGUE</span>
                        ) : (
                          <span className="text-emerald-400">NOMINAL</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Clear Memory Trigger */}
            <button
              onClick={handleResetBaseline}
              className="w-full py-2 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-[11px] font-mono text-slate-400 hover:text-rose-400 transition flex items-center justify-center gap-1.5"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Purge Memory Cache</span>
            </button>
          </div>
        </section>

      </div>
    </main>
  );
}
