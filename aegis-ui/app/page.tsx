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
  Bed,
  RefreshCw,
  Sparkles,
  AlertTriangle,
  Radio,
  Cpu
} from "lucide-react";

interface VitalsState {
  heartRate: number;
  rmssd: number;
  temperature: number;
  tempSlope: number;
  eda: number;
  riskLevel: string;
  isAnomaly: boolean;
}

interface MessageLog {
  id: string;
  sender: "user" | "baymax";
  text: string;
  timestamp: string;
  isAlert?: boolean;
}

const BACKEND_URL = "http://127.0.0.1:8000";

export default function BaymaxCompanionDashboard() {
  // Biometrics State
  const [vitals, setVitals] = useState<VitalsState>({
    heartRate: 72,
    rmssd: 45,
    temperature: 36.8,
    tempSlope: 0.0,
    eda: 1.5,
    riskLevel: "OPTIMAL",
    isAnomaly: false,
  });

  // Companion State
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(true);
  const [avatarState, setAvatarState] = useState<"idle" | "listening" | "speaking" | "alert">("idle");
  const [transcript, setTranscript] = useState<string>("");
  const [messages, setMessages] = useState<MessageLog[]>([
    {
      id: "init-1",
      sender: "baymax",
      text: "Hello, I am Baymax, your personal healthcare companion. Your physiological parameters are currently within normal baseline limits.",
      timestamp: "12:00",
    },
  ]);
  const [cooldownActive, setCooldownActive] = useState<boolean>(false);
  const [escalationsCount, setEscalationsCount] = useState<number>(0);

  const recognitionRef = useRef<any>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Initialize Speech Recognition
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
          setTranscript(spokenText);
          handleUserSpeech(spokenText);
        };

        reco.onerror = () => {
          setIsListening(false);
          setAvatarState(vitals.isAnomaly ? "alert" : "idle");
        };

        reco.onend = () => {
          setIsListening(false);
          if (!isSpeaking) {
            setAvatarState(vitals.isAnomaly ? "alert" : "idle");
          }
        };

        recognitionRef.current = reco;
      }
    }
  }, [vitals.isAnomaly, isSpeaking]);

  // Scroll to bottom on new message
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
    utterance.rate = 0.95; // Calm, gentle cadence
    utterance.pitch = 1.05; // Friendly companion pitch

    // Prefer a soothing voice if available
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
      setAvatarState(vitals.isAnomaly ? "alert" : "speaking");
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setAvatarState(vitals.isAnomaly ? "alert" : "idle");
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      setAvatarState(vitals.isAnomaly ? "alert" : "idle");
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
        // Fallback simulated voice prompt if mic is restricted
        const sampleQueries = [
          "How are my vitals doing right now Baymax?",
          "Can you scan my physiological status?",
          "Should I drink more water?",
        ];
        const randomQ = sampleQueries[Math.floor(Math.random() * sampleQueries.length)];
        handleUserSpeech(randomQ);
      }
    }
  };

  // Interact with Backend
  const handleUserSpeech = async (speechText: string) => {
    const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);

    // Append user message
    setMessages((prev) => [
      ...prev,
      { id: `user-${Date.now()}`, sender: "user", text: speechText, timestamp: timeStr },
    ]);

    try {
      const res = await fetch(`${BACKEND_URL}/companion-interact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_speech: speechText,
          heart_rate: vitals.heartRate,
          rmssd: vitals.rmssd,
          temperature: vitals.temperature,
          temp_slope: vitals.tempSlope,
          eda: vitals.eda,
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
            isAlert: data.is_anomaly,
          },
        ]);

        if (data.is_anomaly) {
          setEscalationsCount((c) => c + 1);
          setCooldownActive(true);
        }

        speakText(reply);
      } else {
        throw new Error("HTTP error");
      }
    } catch {
      // Local fallback
      const reply = vitals.isAnomaly
        ? "I detect an acute elevation in your thermal baseline and sympathetic arousal. Please rest immediately and begin a cooldown protocol."
        : "Your physiological parameters indicate optimal equilibrium. Your heart rate and HRV are in healthy resting alignment.";

      setMessages((prev) => [
        ...prev,
        {
          id: `baymax-${Date.now()}`,
          sender: "baymax",
          text: reply,
          timestamp: timeStr,
          isAlert: vitals.isAnomaly,
        },
      ]);
      speakText(reply);
    }
  };

  // God Mode Anomaly Spike Trigger
  const handleInjectAnomaly = async () => {
    const spikeVitals: VitalsState = {
      heartRate: 135,
      rmssd: 15,
      temperature: 39.5,
      tempSlope: 0.15,
      eda: 8.5,
      riskLevel: "HIGH RISK",
      isAnomaly: true,
    };

    setVitals(spikeVitals);
    setAvatarState("alert");
    setCooldownActive(true);
    setEscalationsCount((c) => c + 1);

    const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
    const alertSpeech =
      "I detect an acute elevation in your thermal baseline and autonomic arousal. Let us begin a cooldown protocol immediately.";

    setMessages((prev) => [
      ...prev,
      {
        id: `alert-${Date.now()}`,
        sender: "baymax",
        text: alertSpeech,
        timestamp: timeStr,
        isAlert: true,
      },
    ]);

    // Send to backend to trigger n8n escalation
    try {
      fetch(`${BACKEND_URL}/companion-interact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_speech: "INJECT_ANOMALY_TRIGGER",
          heart_rate: spikeVitals.heartRate,
          rmssd: spikeVitals.rmssd,
          temperature: spikeVitals.temperature,
          temp_slope: spikeVitals.tempSlope,
          eda: spikeVitals.eda,
        }),
      });
    } catch {
      // Background trigger
    }

    // Proactive Voice Takeover
    speakText(alertSpeech);
  };

  // Reset to Baseline
  const handleResetBaseline = () => {
    const normalVitals: VitalsState = {
      heartRate: 72,
      rmssd: 45,
      temperature: 36.8,
      tempSlope: 0.0,
      eda: 1.5,
      riskLevel: "OPTIMAL",
      isAnomaly: false,
    };
    setVitals(normalVitals);
    setAvatarState("idle");
    setCooldownActive(false);

    const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
    const msg = "Biometric equilibrium restored. Resting vital parameters stabilized.";
    setMessages((prev) => [
      ...prev,
      { id: `reset-${Date.now()}`, sender: "baymax", text: msg, timestamp: timeStr },
    ]);
    speakText(msg);
  };

  return (
    <main className="min-h-screen bg-[#05080f] text-slate-100 p-3 sm:p-6 flex items-center justify-center font-sans">
      {/* Mobile-First Companion Chassis */}
      <div className="w-full max-w-md bg-slate-900/70 border border-slate-800/90 rounded-[2.5rem] p-5 shadow-[0_0_50px_rgba(0,0,0,0.8)] backdrop-blur-xl relative overflow-hidden flex flex-col gap-5">
        
        {/* Background Ambient Glow */}
        <div
          className={`absolute -top-24 -left-24 w-64 h-64 rounded-full blur-[90px] transition-all duration-700 pointer-events-none ${
            vitals.isAnomaly
              ? "bg-rose-600/30"
              : "bg-cyan-500/20"
          }`}
        />
        <div
          className={`absolute -bottom-24 -right-24 w-64 h-64 rounded-full blur-[90px] transition-all duration-700 pointer-events-none ${
            vitals.isAnomaly
              ? "bg-amber-600/25"
              : "bg-emerald-500/15"
          }`}
        />

        {/* Top Header */}
        <header className="flex justify-between items-center z-10">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full bg-cyan-950/80 border border-cyan-400/40 flex items-center justify-center text-cyan-300 shadow-[0_0_10px_rgba(6,182,212,0.5)]">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-wider text-white flex items-center gap-1.5">
                BAYMAX <span className="text-[10px] text-cyan-400 font-mono font-normal">SIH26181</span>
              </h1>
              <p className="text-[10px] text-slate-400 font-mono">Personal Healthcare Companion</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Voice Toggle */}
            <button
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className={`p-2 rounded-full border transition ${
                voiceEnabled
                  ? "bg-cyan-950/60 border-cyan-500/40 text-cyan-300"
                  : "bg-slate-800 border-slate-700 text-slate-500"
              }`}
              title={voiceEnabled ? "Voice Enabled" : "Voice Muted"}
            >
              {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </button>

            {/* Quick God Mode Trigger */}
            <button
              id="inject-anomaly-btn"
              onClick={vitals.isAnomaly ? handleResetBaseline : handleInjectAnomaly}
              className={`px-3 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1.5 transition-all shadow-md ${
                vitals.isAnomaly
                  ? "bg-emerald-950 border border-emerald-500 text-emerald-300 hover:bg-emerald-900"
                  : "bg-rose-950/90 border border-rose-500/70 text-rose-300 hover:bg-rose-900 hover:text-white"
              }`}
              title="Force Anomaly Spike"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>{vitals.isAnomaly ? "RESET" : "SPIKE"}</span>
            </button>
          </div>
        </header>

        {/* Animated Baymax Avatar Core */}
        <section className="flex flex-col items-center justify-center py-2 z-10 relative">
          <div className="relative flex items-center justify-center">
            {/* Ambient Animated Rings */}
            <div
              className={`absolute w-36 h-36 rounded-full transition-all duration-700 ${
                avatarState === "alert"
                  ? "border-2 border-rose-500/80 animate-ping opacity-60"
                  : avatarState === "listening"
                  ? "border-2 border-cyan-400 animate-pulse opacity-70 scale-110"
                  : "border border-cyan-500/20 animate-pulse"
              }`}
            />
            <div
              className={`absolute w-44 h-44 rounded-full transition-all duration-700 ${
                avatarState === "alert"
                  ? "bg-rose-500/10 blur-xl animate-pulse"
                  : avatarState === "listening"
                  ? "bg-cyan-500/15 blur-xl"
                  : "bg-cyan-500/5 blur-md"
              }`}
            />

            {/* Baymax Avatar Face Container */}
            <div
              className={`w-28 h-28 rounded-full border-2 flex flex-col items-center justify-center shadow-2xl transition-all duration-500 relative bg-slate-950/90 ${
                avatarState === "alert"
                  ? "border-rose-500 shadow-[0_0_35px_rgba(244,63,94,0.6)]"
                  : avatarState === "listening"
                  ? "border-cyan-400 shadow-[0_0_30px_rgba(6,182,212,0.6)]"
                  : "border-slate-700 shadow-[0_0_20px_rgba(6,182,212,0.3)]"
              }`}
            >
              {/* Baymax Eyes & Connecting Bridge Line */}
              <div className="flex items-center justify-center gap-6 mt-1">
                {/* Left Eye */}
                <div
                  className={`w-3.5 h-3.5 rounded-full transition-all duration-300 ${
                    avatarState === "alert"
                      ? "bg-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.9)]"
                      : "bg-white shadow-[0_0_8px_rgba(255,255,255,0.9)]"
                  }`}
                />
                
                {/* Connecting Eye Line */}
                <div
                  className={`w-8 h-[2px] -mx-4 transition-all duration-300 ${
                    avatarState === "alert" ? "bg-rose-400/80" : "bg-white/80"
                  }`}
                />

                {/* Right Eye */}
                <div
                  className={`w-3.5 h-3.5 rounded-full transition-all duration-300 ${
                    avatarState === "alert"
                      ? "bg-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.9)]"
                      : "bg-white shadow-[0_0_8px_rgba(255,255,255,0.9)]"
                  }`}
                />
              </div>

              {/* Status Pill beneath Avatar */}
              <div className="absolute -bottom-2.5 px-2.5 py-0.5 rounded-full bg-slate-900 border border-slate-700 text-[9px] font-mono tracking-wider uppercase text-slate-300">
                {avatarState === "alert" ? (
                  <span className="text-rose-400 font-bold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
                    ALERT PROTOCOL
                  </span>
                ) : avatarState === "listening" ? (
                  <span className="text-cyan-300 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span>
                    LISTENING...
                  </span>
                ) : avatarState === "speaking" ? (
                  <span className="text-cyan-300">SPEAKING</span>
                ) : (
                  <span className="text-emerald-400">READY</span>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Tri-Ring Vitals Arc Display */}
        <section className="grid grid-cols-3 gap-2.5 z-10">
          {/* Heart Rate Arc Card */}
          <div className="p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col items-center text-center relative">
            <div className="relative w-14 h-14 flex items-center justify-center mb-1">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="14" fill="none" stroke="#1e293b" strokeWidth="3" />
                <circle
                  cx="18"
                  cy="18"
                  r="14"
                  fill="none"
                  stroke={vitals.heartRate > 100 ? "#f43f5e" : "#06b6d4"}
                  strokeWidth="3.2"
                  strokeDasharray={`${Math.min(100, (vitals.heartRate / 160) * 100)} 100`}
                  strokeLinecap="round"
                  className="transition-all duration-700"
                />
              </svg>
              <Heart className={`w-4 h-4 absolute ${vitals.heartRate > 100 ? "text-rose-400 animate-bounce" : "text-cyan-400 animate-pulse"}`} />
            </div>
            <span className={`text-base font-black font-mono leading-none ${vitals.heartRate > 100 ? "text-rose-400" : "text-white"}`}>
              {vitals.heartRate}
            </span>
            <span className="text-[9px] text-slate-400 font-mono mt-0.5">HR (BPM)</span>
          </div>

          {/* HRV / RMSSD Arc Card */}
          <div className="p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col items-center text-center relative">
            <div className="relative w-14 h-14 flex items-center justify-center mb-1">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="14" fill="none" stroke="#1e293b" strokeWidth="3" />
                <circle
                  cx="18"
                  cy="18"
                  r="14"
                  fill="none"
                  stroke={vitals.rmssd < 20 ? "#f43f5e" : "#10b981"}
                  strokeWidth="3.2"
                  strokeDasharray={`${Math.min(100, (vitals.rmssd / 60) * 100)} 100`}
                  strokeLinecap="round"
                  className="transition-all duration-700"
                />
              </svg>
              <Activity className={`w-4 h-4 absolute ${vitals.rmssd < 20 ? "text-rose-400" : "text-emerald-400"}`} />
            </div>
            <span className={`text-base font-black font-mono leading-none ${vitals.rmssd < 20 ? "text-rose-400" : "text-emerald-300"}`}>
              {vitals.rmssd}
            </span>
            <span className="text-[9px] text-slate-400 font-mono mt-0.5">HRV (ms)</span>
          </div>

          {/* Core Temperature Arc Card */}
          <div className="p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col items-center text-center relative">
            <div className="relative w-14 h-14 flex items-center justify-center mb-1">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="14" fill="none" stroke="#1e293b" strokeWidth="3" />
                <circle
                  cx="18"
                  cy="18"
                  r="14"
                  fill="none"
                  stroke={vitals.temperature > 38.0 ? "#f43f5e" : "#f59e0b"}
                  strokeWidth="3.2"
                  strokeDasharray={`${Math.min(100, ((vitals.temperature - 35) / 6) * 100)} 100`}
                  strokeLinecap="round"
                  className="transition-all duration-700"
                />
              </svg>
              <Thermometer className={`w-4 h-4 absolute ${vitals.temperature > 38.0 ? "text-rose-400 animate-pulse" : "text-amber-400"}`} />
            </div>
            <span className={`text-base font-black font-mono leading-none ${vitals.temperature > 38.0 ? "text-rose-400" : "text-amber-300"}`}>
              {vitals.temperature.toFixed(1)}°
            </span>
            <span className="text-[9px] text-slate-400 font-mono mt-0.5">TEMP (°C)</span>
          </div>
        </section>

        {/* Proactive Care Guidance Feed / Chat */}
        <section className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-3 flex flex-col h-48 overflow-y-auto z-10 shadow-inner">
          <div className="text-[10px] text-slate-500 font-mono mb-2 flex items-center justify-between border-b border-slate-800/60 pb-1">
            <span className="flex items-center gap-1">
              <Cpu className="w-3 h-3 text-cyan-400" />
              VOICE COMPANION FEED
            </span>
            <span className="text-emerald-400 text-[9px] font-mono">WESAD ACTIVE</span>
          </div>

          <div className="space-y-2.5 flex-1 text-xs">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.sender === "user" ? "items-end" : "items-start"
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3 py-2 leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-cyan-950/80 text-cyan-100 border border-cyan-500/40 rounded-br-none"
                      : msg.isAlert
                      ? "bg-rose-950/90 text-rose-100 border border-rose-500/60 rounded-bl-none shadow-[0_0_15px_rgba(244,63,94,0.3)]"
                      : "bg-slate-900 text-slate-200 border border-slate-800 rounded-bl-none"
                  }`}
                >
                  <p>{msg.text}</p>
                </div>
                <span className="text-[9px] text-slate-500 mt-0.5 px-1 font-mono">
                  {msg.timestamp}
                </span>
              </div>
            ))}
            <div ref={chatBottomRef} />
          </div>
        </section>

        {/* Voice Microphone Input Bar */}
        <section className="flex items-center gap-2 z-10">
          <button
            onClick={toggleListening}
            className={`flex-1 py-3 px-4 rounded-2xl border font-mono text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-lg active:scale-98 ${
              isListening
                ? "bg-cyan-500 text-slate-950 border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.8)] animate-pulse"
                : "bg-slate-950 hover:bg-slate-800/80 border-slate-700 text-slate-200"
            }`}
          >
            {isListening ? (
              <>
                <Mic className="w-4 h-4 animate-bounce" />
                <span>Listening... Speak now</span>
              </>
            ) : (
              <>
                <Mic className="w-4 h-4 text-cyan-400" />
                <span>Tap to Speak with Baymax</span>
              </>
            )}
          </button>
        </section>

        {/* Proactive Lifestyle Cards */}
        <section className="grid grid-cols-2 gap-2 text-[11px] font-mono z-10">
          <div className={`p-2.5 rounded-xl border flex items-center gap-2 ${
            vitals.isAnomaly ? "bg-rose-950/40 border-rose-500/40" : "bg-slate-950/50 border-slate-800"
          }`}>
            <Droplets className={`w-4 h-4 ${vitals.isAnomaly ? "text-rose-400" : "text-cyan-400"}`} />
            <div>
              <div className="text-slate-400 text-[9px]">HYDRATION</div>
              <div className={vitals.isAnomaly ? "text-rose-300 font-bold" : "text-slate-200"}>
                {vitals.isAnomaly ? "URGENT REHYDRATE" : "78% Optimal"}
              </div>
            </div>
          </div>

          <div className={`p-2.5 rounded-xl border flex items-center gap-2 ${
            cooldownActive ? "bg-rose-950/40 border-rose-500/40" : "bg-slate-950/50 border-slate-800"
          }`}>
            <Wind className={`w-4 h-4 ${cooldownActive ? "text-rose-400 animate-spin" : "text-emerald-400"}`} />
            <div>
              <div className="text-slate-400 text-[9px]">COOLDOWN</div>
              <div className={cooldownActive ? "text-rose-300 font-bold" : "text-slate-200"}>
                {cooldownActive ? "PROTOCOL ACTIVE" : "Standby"}
              </div>
            </div>
          </div>
        </section>

        {/* Footer info */}
        <footer className="flex justify-between items-center text-[10px] text-slate-500 font-mono pt-1 border-t border-slate-800/50 z-10">
          <span>ESCALATIONS: {escalationsCount}</span>
          <span>AUTONOMOUS SENTINEL</span>
          <span>OFFLINE LLM ACTIVE</span>
        </footer>
      </div>
    </main>
  );
}
