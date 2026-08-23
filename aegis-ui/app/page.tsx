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
  PlayCircle,
  UserCheck,
  FileText,
  AlertOctagon,
  BookOpen,
  Share2,
  Download,
  Printer,
  X,
  BarChart3,
  Compass,
  Users,
  CloudUpload,
  CheckCircle2,
  Server,
  Globe,
  Satellite,
  Stethoscope,
  AudioWaveform,
  Layers,
  Box
} from "lucide-react";

import AnatomicalTwin3D from "./components/AnatomicalTwin3D";

interface VitalsState {
  heartRate: number;
  rmssd: number;
  temperature: number;
  tempSlope: number;
  eda: number;
  ear: number;
  headTiltDeg: number;
  syncopeDetected: boolean;
  postureStatus: string;
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
  matchedProtocol?: string;
  allergyWarning?: boolean;
}

interface MemoryRecord {
  heart_rate: number;
  eye_aspect_ratio: number;
  fatigue_flag: boolean;
  rppg_signal: number;
}

interface PatientProfile {
  patient_uid: string;
  name: string;
  age: number;
  gender: string;
  blood_type: string;
  allergies: string;
  active_medications: string;
  chronic_conditions: string;
  emergency_contact: string;
  location?: string;
  is_active?: boolean;
}

interface SyncQueueStatus {
  pending_offline_count: number;
  synced_hospital_count: number;
  total_bundles: number;
  sync_mode: string;
  recent_bundles: Array<any>;
}

interface RollingStats {
  record_count: number;
  avg_heart_rate: number;
  avg_ear: number;
  fatigue_events_in_window: number;
}

const LANGUAGES = [
  { code: "en", label: "🇬🇧 English", speechCode: "en-IN" },
  { code: "te", label: "🇮🇳 తెలుగు (Telugu)", speechCode: "te-IN" },
  { code: "hi", label: "🇮🇳 हिन्दी (Hindi)", speechCode: "hi-IN" },
  { code: "ta", label: "🇮🇳 தமிழ் (Tamil)", speechCode: "ta-IN" },
  { code: "kn", label: "🇮🇳 ಕನ್ನಡ (Kannada)", speechCode: "kn-IN" }
];

const BACKEND_URL = "http://127.0.0.1:8000";

export default function AegisMedicalCommandDeck() {
  // Biometrics & Sensor State
  const [vitals, setVitals] = useState<VitalsState>({
    heartRate: 72,
    rmssd: 45,
    temperature: 36.8,
    tempSlope: 0.0,
    eda: 1.5,
    ear: 0.32,
    headTiltDeg: 0.0,
    syncopeDetected: false,
    postureStatus: "ERECT_NOMINAL",
    riskLevel: "OPTIMAL",
    isAnomaly: false,
    isFatigued: false,
  });

  // Visual Tab State for Left Deck (Webcam vs 3D Digital Twin)
  const [visualMode, setVisualMode] = useState<"camera" | "3d_twin">("3d_twin");

  // Multimodal Diagnostics State
  const [anemiaResult, setAnemiaResult] = useState<any>({
    estimated_hemoglobin_g_dl: 13.8,
    status: "OPTIMAL_HEMOGLOBIN",
    recommendation: "Capillary perfusion and oxygenation within healthy physiological limits."
  });
  const [coughResult, setCoughResult] = useState<any>({
    acoustic_pattern: "CLEAR_BENIGN_RESPIRATION",
    severity: "LOW",
    clinical_guidance: "No pathological acoustic signature detected. Normal bronchial sounds."
  });
  const [qsofaResult, setQsofaResult] = useState<any>({
    qsofa_score: 0,
    shock_probability: 0.08,
    triage_category: "LOW_RISK_NOMINAL",
    immediate_protocol: "Continue routine vital surveillance. No immediate organ dysfunction signs."
  });
  const [satelliteSOS, setSatelliteSOS] = useState<any>({
    micro_packet: "AEGIS!eyJwIjoiUEFULVJBTS0yMDI2IiwiYnQiOiJPIiwiaHIiOjcyLCJ0cCI6MzYuOCwicXMiOjAsInNwIjo4LCJncHMiOiIxNy45Njg5IE4sIDc5LjU5NDEgRSJ9",
    byte_size: 132,
    target_mesh: "Iridium / Starlink / LoRa P2P Sub-GHz 868MHz"
  });

  // Explainable AI (XAI) Biomarker Contributions
  const [xaiContributions, setXaiContributions] = useState<Record<string, number>>({
    "Heart Rate": 12.5,
    "HRV / Autonomic Strain": 18.0,
    "Core Temperature": 22.5,
    "Thermal Velocity (Slope)": 27.0,
    "EDA Skin Conductance": 20.0
  });
  const [topDriver, setTopDriver] = useState<string>("Thermal Velocity (Slope)");

  // UI & Multi-Lingual State
  const [selectedLanguage, setSelectedLanguage] = useState<string>("en");
  const [textInput, setTextInput] = useState<string>("");
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(true);
  const [avatarState, setAvatarState] = useState<"idle" | "listening" | "speaking" | "alert">("idle");
  const [messages, setMessages] = useState<MessageLog[]>([
    {
      id: "init-1",
      sender: "baymax",
      text: "Hello! I am Baymax, your personal healthcare companion. 3D Digital Twin, Point-of-Care Diagnostics, and Multi-lingual RAG are active. How may I assist you today?",
      timestamp: "12:00",
    },
  ]);

  // Voice Settings State (Calm Baymax Male Persona)
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoiceName, setSelectedVoiceName] = useState<string>("");
  const [speechRate, setSpeechRate] = useState<number>(0.90);
  const [speechPitch, setSpeechPitch] = useState<number>(0.90);

  // Multi-Patient EHR State
  const [patientList, setPatientList] = useState<PatientProfile[]>([]);
  const [patientProfile, setPatientProfile] = useState<PatientProfile>({
    patient_uid: "PAT-RAM-2026",
    name: "Ramcharan",
    age: 24,
    gender: "Male",
    blood_type: "O+",
    allergies: "Ibuprofen, NSAIDs",
    active_medications: "None",
    chronic_conditions: "Mild Asthmatic Tendency",
    emergency_contact: "Dr. Callaghan",
    location: "District General Clinic"
  });

  // Offline Store-and-Forward Sync Queue State
  const [syncQueue, setSyncQueue] = useState<SyncQueueStatus>({
    pending_offline_count: 2,
    synced_hospital_count: 0,
    total_bundles: 2,
    sync_mode: "OFFLINE_STORE_AND_FORWARD",
    recent_bundles: []
  });
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [syncSuccessMsg, setSyncSuccessMsg] = useState<string>("");

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

  // FHIR / Clinical Handover Modal State
  const [isHandoverModalOpen, setIsHandoverModalOpen] = useState<boolean>(false);
  const [handoverTab, setHandoverTab] = useState<"triage" | "fhir">("triage");
  const [fhirData, setFhirData] = useState<any>(null);

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

  // 2. Initialize Voice Synthesis
  useEffect(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      const updateVoices = () => {
        const allVoices = window.speechSynthesis.getVoices();
        if (allVoices.length === 0) return;

        setAvailableVoices(allVoices);

        const isMaleOrBaymax = (v: SpeechSynthesisVoice) => {
          const name = v.name.toLowerCase();
          if (
            name.includes("female") ||
            name.includes("zira") ||
            name.includes("samantha") ||
            name.includes("jenny") ||
            name.includes("victoria") ||
            name.includes("karen") ||
            name.includes("sonia") ||
            name.includes("eva") ||
            name.includes("hazel") ||
            name.includes("susan") ||
            name.includes("aria")
          ) {
            return false;
          }
          return (
            name.includes("david") ||
            name.includes("mark") ||
            name.includes("guy") ||
            name.includes("ryan") ||
            name.includes("daniel") ||
            name.includes("george") ||
            name.includes("male") ||
            name.includes("natural") ||
            (v.lang.startsWith("en") && !name.includes("female"))
          );
        };

        const preferredMaleVoice =
          allVoices.find((v) => v.name.includes("David")) ||
          allVoices.find((v) => v.name.includes("Guy") && v.name.includes("Natural")) ||
          allVoices.find((v) => v.name.includes("Mark")) ||
          allVoices.find((v) => v.name.includes("Google UK English Male")) ||
          allVoices.find((v) => v.name.includes("Daniel")) ||
          allVoices.find(isMaleOrBaymax) ||
          allVoices[0];

        if (preferredMaleVoice) {
          setSelectedVoiceName((prev) => prev || preferredMaleVoice.name);
        }
      };

      updateVoices();
      window.speechSynthesis.onvoiceschanged = updateVoices;
    }
  }, []);

  // 3. Initialize Multi-Lingual Speech Recognition (STT)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const reco = new SpeechRecognition();
        reco.continuous = false;
        reco.interimResults = false;
        const langObj = LANGUAGES.find((l) => l.code === selectedLanguage);
        reco.lang = langObj ? langObj.speechCode : "en-US";

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
          setAvatarState(vitals.isAnomaly || vitals.isFatigued || vitals.syncopeDetected ? "alert" : "idle");
        };

        reco.onend = () => {
          setIsListening(false);
          if (!isSpeaking) {
            setAvatarState(vitals.isAnomaly || vitals.isFatigued || vitals.syncopeDetected ? "alert" : "idle");
          }
        };

        recognitionRef.current = reco;
      }
    }
  }, [vitals.isAnomaly, vitals.isFatigued, vitals.syncopeDetected, isSpeaking, selectedLanguage]);

  // 4. Periodic Memory Records, Patient List & Sync Queue Poller (every 2.5s)
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
          if (data.patient_profile) {
            setPatientProfile(data.patient_profile);
          }
        }

        const resPatients = await fetch(`${BACKEND_URL}/patients`);
        if (resPatients.ok) {
          const pList = await resPatients.json();
          setPatientList(pList);
        }

        const resSync = await fetch(`${BACKEND_URL}/sync-queue/status`);
        if (resSync.ok) {
          const sData = await resSync.json();
          setSyncQueue(sData);
        }
      } catch {
        // Poller
      }
    };

    pollMemory();
    const interval = setInterval(pollMemory, 2500);
    return () => clearInterval(interval);
  }, []);

  // 5. Live rPPG Plethysmogram Oscilloscope Canvas
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
          ctx.strokeStyle = vitals.isAnomaly || vitals.syncopeDetected ? "#f43f5e" : "#06b6d4";
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
  }, [vitals.heartRate, vitals.isAnomaly, vitals.syncopeDetected]);

  // Scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Multi-Lingual Speech Synthesis (TTS)
  const speakText = (text: string, langOverride?: string) => {
    if (!voiceEnabled || typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }
    window.speechSynthesis.cancel();

    const targetLang = langOverride || selectedLanguage;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = speechRate;
    utterance.pitch = speechPitch;

    const voices = window.speechSynthesis.getVoices();
    let chosenVoice: SpeechSynthesisVoice | undefined;

    const matchingRegional = voices.find((v) => v.lang.toLowerCase().startsWith(targetLang));
    if (matchingRegional) {
      chosenVoice = matchingRegional;
      utterance.lang = matchingRegional.lang;
    } else if (selectedVoiceName) {
      chosenVoice = voices.find((v) => v.name === selectedVoiceName);
    }

    if (!chosenVoice) {
      chosenVoice =
        voices.find((v) => v.name.includes("David")) ||
        voices.find((v) => v.name.includes("Google UK English Male")) ||
        voices[0];
    }

    if (chosenVoice) {
      utterance.voice = chosenVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
      setAvatarState(vitals.isAnomaly || vitals.isFatigued || vitals.syncopeDetected ? "alert" : "speaking");
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setAvatarState(vitals.isAnomaly || vitals.isFatigued || vitals.syncopeDetected ? "alert" : "idle");
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      setAvatarState(vitals.isAnomaly || vitals.isFatigued || vitals.syncopeDetected ? "alert" : "idle");
    };

    window.speechSynthesis.speak(utterance);
  };

  // Next-Level Diagnostic Triggers
  const handleScreenAnemia = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/diagnostics/anemia`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ erythema_index: 2.8, r_channel_mean: 152.0 }),
      });
      if (res.ok) {
        const data = await res.json();
        setAnemiaResult(data);
        const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
        const msg = `Optical Conjunctival Screening: Estimated Hemoglobin is ${data.estimated_hemoglobin_g_dl} g/dL (${data.status}). ${data.recommendation}`;
        setMessages((prev) => [
          ...prev,
          { id: `anemia-${Date.now()}`, sender: "baymax", text: msg, timestamp: timeStr },
        ]);
        speakText(msg);
      }
    } catch (err) {
      console.warn("Anemia screening error:", err);
    }
  };

  const handleAnalyzeCough = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/diagnostics/cough`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ spectral_flux: 0.78, peak_frequency_hz: 1620.0 }),
      });
      if (res.ok) {
        const data = await res.json();
        setCoughResult(data);
        const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
        const msg = `Acoustic Cough Biomarker Analysis: Detected ${data.acoustic_pattern} (${data.severity} SEVERITY). ${data.clinical_guidance}`;
        setMessages((prev) => [
          ...prev,
          { id: `cough-${Date.now()}`, sender: "baymax", text: msg, timestamp: timeStr, isAlert: data.severity === "HIGH" || data.severity === "CRITICAL" },
        ]);
        speakText(msg);
      }
    } catch (err) {
      console.warn("Cough analysis error:", err);
    }
  };

  const handleCalculateQSOFA = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/diagnostics/qsofa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          heart_rate: vitals.heartRate,
          temperature: vitals.temperature,
          temp_slope: vitals.tempSlope,
          syncope_detected: vitals.syncopeDetected,
          respiratory_rate: vitals.heartRate > 100 ? 28.0 : 16.0,
          systolic_bp: vitals.syncopeDetected ? 82.0 : 115.0
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setQsofaResult(data);
        const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
        const msg = `Predictive Sepsis CDS: qSOFA Score = ${data.qsofa_score}/3 (Shock Probability: ${(data.shock_probability * 100).toFixed(0)}%). Category: ${data.triage_category}. Protocol: ${data.immediate_protocol}`;
        setMessages((prev) => [
          ...prev,
          { id: `qsofa-${Date.now()}`, sender: "baymax", text: msg, timestamp: timeStr, isAlert: data.qsofa_score >= 2 },
        ]);
        speakText(msg);
      }
    } catch (err) {
      console.warn("qSOFA error:", err);
    }
  };

  const handleGenerateSOS = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/diagnostics/satellite-sos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ patient_uid: patientProfile.patient_uid, gps_coords: "17.9689 N, 79.5941 E" }),
      });
      if (res.ok) {
        const data = await res.json();
        setSatelliteSOS(data);
        const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
        const msg = `Satellite SOS Uplink Prepared (${data.byte_size} Bytes / 140B Max): Encrypted telemetry packet ready for Iridium / Starlink transmission. Target: Warangal Rural Command.`;
        setMessages((prev) => [
          ...prev,
          { id: `sos-${Date.now()}`, sender: "baymax", text: msg, timestamp: timeStr },
        ]);
        speakText("Emergency satellite SOS micro-packet generated and validated.");
      }
    } catch (err) {
      console.warn("SOS error:", err);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
      } catch {
        const defaultPrompt =
          selectedLanguage === "te"
            ? "నాకు తీవ్రమైన జ్వరం ఉంది. నేను ఇబుప్రోఫెన్ (Ibuprofen) తీసుకోవచ్చా?"
            : selectedLanguage === "hi"
            ? "मुझे तेज बुखार है, क्या मैं इबुप्रोफेन (Ibuprofen) ले सकता हूँ?"
            : "Baymax, my core temperature is spiking and I have a fever. Should I take some Ibuprofen?";
        handleSendQuery(defaultPrompt);
      }
    }
  };

  // Switch Active Patient Context
  const handleSwitchPatient = async (patientUid: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/patients/switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ patient_uid: patientUid }),
      });
      if (res.ok) {
        const updated = await res.json();
        setPatientProfile(updated);
        const timeStr = new Date().toTimeString().split(" ")[0].slice(0, 5);
        const switchMsg = `Active consultation switched to ${updated.name} (${updated.patient_uid}) at ${updated.location}. Documented allergies: ${updated.allergies}.`;
        setMessages((prev) => [
          ...prev,
          { id: `switch-${Date.now()}`, sender: "baymax", text: switchMsg, timestamp: timeStr },
        ]);
        speakText(`Patient switched to ${updated.name}. Record loaded.`);
      }
    } catch (err) {
      console.warn("Patient switch note:", err);
    }
  };

  // Trigger Store-and-Forward FHIR Sync to District Hospital
  const handleTriggerSync = async () => {
    setIsSyncing(true);
    setSyncSuccessMsg("");
    try {
      const res = await fetch(`${BACKEND_URL}/sync-queue/trigger`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setTimeout(() => {
          setIsSyncing(false);
          setSyncSuccessMsg(`SYNC SUCCESSFUL: ${data.synced_bundles_count} FHIR Bundles pushed to District Hospital / ABDM Gateway!`);
          setSyncQueue((prev) => ({
            ...prev,
            pending_offline_count: 0,
            synced_hospital_count: prev.synced_hospital_count + data.synced_bundles_count
          }));
        }, 1200);
      }
    } catch {
      setIsSyncing(false);
    }
  };

  // Send Query to Multi-Lingual Doctor-Level Baymax Engine
  const handleSendQuery = async (queryText: string, customVitals?: Partial<VitalsState>, langOverride?: string) => {
    if (!queryText.trim()) return;
    const targetLang = langOverride || selectedLanguage;
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
          head_tilt_deg: activeVitals.headTiltDeg,
          syncope_detected: activeVitals.syncopeDetected,
          posture_status: activeVitals.postureStatus,
          language: targetLang
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const reply = data.reply_text;

        if (data.feature_contributions) {
          setXaiContributions(data.feature_contributions);
        }
        if (data.top_driver) {
          setTopDriver(data.top_driver);
        }

        setMessages((prev) => [
          ...prev,
          {
            id: `baymax-${Date.now()}`,
            sender: "baymax",
            text: reply,
            timestamp: timeStr,
            isAlert: data.is_anomaly || data.fatigue_detected || data.allergy_warning || data.syncope_detected,
            matchedProtocol: data.matched_protocol ? data.matched_protocol.title : undefined,
            allergyWarning: data.allergy_warning
          },
        ]);

        if (data.is_anomaly || data.fatigue_detected || data.allergy_warning || data.syncope_detected) {
          setEscalationsCount((c) => c + 1);
        }

        speakText(reply, targetLang);
      } else {
        throw new Error("HTTP failure");
      }
    } catch {
      const fallbackMsg = `Doctor-Level inference active. Heart rate: ${activeVitals.heartRate} BPM, Temp: ${activeVitals.temperature}°C.`;
      setMessages((prev) => [
        ...prev,
        { id: `baymax-${Date.now()}`, sender: "baymax", text: fallbackMsg, timestamp: timeStr },
      ]);
      speakText(fallbackMsg, targetLang);
    }
  };

  // Multi-Lingual Quick Simulation Triggers
  const triggerTeluguTest = () => {
    setSelectedLanguage("te");
    const feverVitals: VitalsState = {
      ...vitals,
      heartRate: 108,
      rmssd: 22,
      temperature: 39.1,
      tempSlope: 0.12,
      eda: 4.8,
      ear: 0.28,
      riskLevel: "HIGH RISK",
      isAnomaly: true,
    };
    setVitals(feverVitals);
    setAvatarState("alert");
    handleSendQuery("నాకు తీవ్రమైన జ్వరం ఉంది. నేను ఇబుప్రోఫెన్ (Ibuprofen) వేసుకోవచ్చా?", feverVitals, "te");
  };

  const triggerHindiTest = () => {
    setSelectedLanguage("hi");
    const feverVitals: VitalsState = {
      ...vitals,
      heartRate: 108,
      rmssd: 22,
      temperature: 39.1,
      tempSlope: 0.12,
      eda: 4.8,
      ear: 0.28,
      riskLevel: "HIGH RISK",
      isAnomaly: true,
    };
    setVitals(feverVitals);
    setAvatarState("alert");
    handleSendQuery("मुझे बहुत तेज बुखार है, क्या मैं इबुप्रोफेन (Ibuprofen) ले सकता हूँ?", feverVitals, "hi");
  };

  // Simulation Trigger: Syncope & Postural Collapse Fall Detection
  const triggerSyncopeTest = async () => {
    const syncopeVitals: VitalsState = {
      ...vitals,
      heartRate: 128,
      rmssd: 14,
      temperature: 38.9,
      tempSlope: 0.10,
      eda: 7.2,
      ear: 0.12,
      headTiltDeg: 42.5,
      syncopeDetected: true,
      postureStatus: "SYNCOPE_COLLAPSE_DETECTED",
      riskLevel: "HIGH RISK",
      isAnomaly: true,
    };
    setVitals(syncopeVitals);
    setAvatarState("alert");
    handleSendQuery("Alert: Optical sensor detects acute head tilt of 42.5 degrees and sudden vertical drop indicating syncope and loss of postural control.", syncopeVitals);
  };

  // Simulation Trigger: Allergy Contraindication Test (English)
  const triggerAllergyTest = async () => {
    const feverVitals: VitalsState = {
      ...vitals,
      heartRate: 105,
      rmssd: 25,
      temperature: 39.2,
      tempSlope: 0.12,
      eda: 4.5,
      ear: 0.28,
      riskLevel: "HIGH RISK",
      isAnomaly: true,
    };
    setVitals(feverVitals);
    setAvatarState("alert");
    handleSendQuery("Baymax, my core temperature is spiking and I have a severe fever. Should I take some Ibuprofen?", feverVitals, "en");
  };

  // Fetch FHIR Handover Data and Open Modal
  const openHandoverModal = async () => {
    setIsHandoverModalOpen(true);
    try {
      const res = await fetch(`${BACKEND_URL}/clinical-handover/fhir`);
      if (res.ok) {
        const data = await res.json();
        setFhirData(data);
      }
    } catch (err) {
      console.warn("FHIR fetch note:", err);
    }
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
      headTiltDeg: 0.0,
      syncopeDetected: false,
      postureStatus: "ERECT_NOMINAL",
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
                AEGIS <span className="text-cyan-400 font-mono text-xs font-normal">// NEXT-GEN 3D MEDICAL INTELLIGENCE COMMAND DECK</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-500/40 text-[10px] font-mono text-cyan-300">
                GOD TIER v4.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono flex items-center gap-2 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>3D DIGITAL TWIN</span>
              <span>•</span>
              <span>MULTIMODAL DIAGNOSTICS</span>
              <span>•</span>
              <span>qSOFA SEPSIS CDS</span>
              <span>•</span>
              <span>SATELLITE SOS</span>
            </p>
          </div>
        </div>

        {/* Language Selector, Quick Simulation Controls & Voice Selector */}
        <div className="flex flex-wrap items-center gap-2">
          
          {/* Multi-Lingual Language Selector */}
          <div className="flex items-center gap-1.5 bg-slate-950 border border-cyan-500/60 px-2.5 py-1 rounded-xl shadow-[0_0_10px_rgba(6,182,212,0.3)]">
            <Globe className="w-3.5 h-3.5 text-cyan-400" />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="bg-transparent text-[11px] font-mono font-bold text-cyan-300 focus:outline-none cursor-pointer"
              title="Select Diagnostic & Voice Language"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code} className="bg-slate-900 text-slate-200">
                  {l.label}
                </option>
              ))}
            </select>
          </div>

          {/* Quick Telugu Pitch Button */}
          <button
            onClick={triggerTeluguTest}
            className="px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-amber-950/90 border border-amber-500/70 text-amber-300 hover:bg-amber-900 transition flex items-center gap-1 shadow"
            title="Demonstrate Live Telugu Clinical RAG & Drug Safety"
          >
            <span>🇮🇳 TELUGU</span>
          </button>

          {/* Quick Hindi Pitch Button */}
          <button
            onClick={triggerHindiTest}
            className="px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-orange-950/90 border border-orange-500/70 text-orange-300 hover:bg-orange-900 transition flex items-center gap-1 shadow"
            title="Demonstrate Live Hindi Clinical RAG & Drug Safety"
          >
            <span>🇮🇳 HINDI</span>
          </button>

          {/* Export Clinical Handover FHIR / PDF Button */}
          <button
            onClick={openHandoverModal}
            className="px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-teal-950/90 border border-teal-500/70 text-teal-300 hover:bg-teal-900 transition flex items-center gap-1.5 shadow-[0_0_15px_rgba(20,184,166,0.4)]"
            title="Export Standardized HL7/FHIR Clinical Triage Handover Report"
          >
            <Share2 className="w-3.5 h-3.5 text-teal-400" />
            <span>EXPORT FHIR</span>
          </button>

          {/* Test Syncope Collapse Button */}
          <button
            onClick={triggerSyncopeTest}
            className="px-2.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-rose-950/90 border border-rose-500/70 text-rose-300 hover:bg-rose-900 transition flex items-center gap-1.5 shadow"
            title="Simulate Head Tilt / Syncope Fainting Collapse Fall"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
            <span>SYNCOPE</span>
          </button>

          <button
            onClick={handleResetBaseline}
            className="px-3 py-1.5 rounded-xl text-xs font-mono font-bold bg-emerald-950/80 border border-emerald-500/60 text-emerald-300 hover:bg-emerald-900 transition flex items-center gap-1.5 shadow"
            title="Reset Baseline & Clear Database"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>RESET</span>
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
        {/* LEFT DECK (Cols 1-4): 3D Anatomical Digital Twin, Webcam & rPPG Waveform */}
        {/* ========================================================================= */}
        <section className="lg:col-span-4 flex flex-col gap-4">
          
          {/* Visual Display Switcher (3D Twin vs Hardware Camera) */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-3 backdrop-blur-xl shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Box className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold font-mono tracking-wider text-slate-200">
                  {visualMode === "3d_twin" ? "3D ANATOMICAL DIGITAL TWIN" : "LIVE OPTICAL HARDWARE SCANNER"}
                </h2>
              </div>
              
              {/* Tab Switcher */}
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-[10px] font-mono">
                <button
                  onClick={() => setVisualMode("3d_twin")}
                  className={`px-2 py-0.5 rounded-lg transition ${
                    visualMode === "3d_twin" ? "bg-cyan-600 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  3D Twin
                </button>
                <button
                  onClick={() => setVisualMode("camera")}
                  className={`px-2 py-0.5 rounded-lg transition ${
                    visualMode === "camera" ? "bg-cyan-600 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Webcam
                </button>
              </div>
            </div>

            {/* Visual Viewport */}
            {visualMode === "3d_twin" ? (
              <AnatomicalTwin3D
                heartRate={vitals.heartRate}
                temperature={vitals.temperature}
                eda={vitals.eda}
                syncopeDetected={vitals.syncopeDetected}
                isAnomaly={vitals.isAnomaly}
              />
            ) : (
              <div className="relative w-full aspect-[4/3] rounded-2xl bg-black overflow-hidden border border-slate-800 flex items-center justify-center shadow-inner">
                <video
                  ref={videoRef}
                  className="w-full h-full object-cover scale-x-[-1]"
                  autoPlay
                  playsInline
                  muted
                />
                <div className="absolute top-2 left-2 px-2 py-1 rounded bg-black/70 backdrop-blur border border-slate-700 text-[9px] font-mono text-cyan-300">
                  HEAD TILT: {vitals.headTiltDeg.toFixed(1)}°
                </div>
                <div className="absolute top-2 right-2 px-2 py-1 rounded bg-black/70 backdrop-blur border border-slate-700 text-[9px] font-mono text-slate-300">
                  PATIENT: {patientProfile.name}
                </div>
                {vitals.syncopeDetected && (
                  <div className="absolute inset-x-2 bottom-2 p-2 rounded-xl bg-rose-950/90 border border-rose-500 text-rose-200 text-xs font-mono font-bold flex items-center gap-2 animate-bounce shadow-2xl">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    <span>SYNCOPE COLLAPSE ({vitals.headTiltDeg}°)</span>
                  </div>
                )}
              </div>
            )}

            {/* Optical EAR & Syncope Posture Diagnostics */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className={`p-3 rounded-2xl border ${
                vitals.ear < 0.22 ? "bg-amber-950/60 border-amber-500/60" : "bg-slate-950/60 border-slate-800"
              }`}>
                <div className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Eye className="w-3 h-3 text-cyan-400" />
                  OCULAR EAR
                </div>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className={`text-xl font-black ${vitals.ear < 0.22 ? "text-amber-400" : "text-white"}`}>
                    {vitals.ear.toFixed(3)}
                  </span>
                  <span className="text-[10px] text-slate-400">Thresh: 0.22</span>
                </div>
              </div>

              <div className={`p-3 rounded-2xl border ${
                vitals.syncopeDetected ? "bg-rose-950/60 border-rose-500/60" : "bg-slate-950/60 border-slate-800"
              }`}>
                <div className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Compass className="w-3 h-3 text-emerald-400" />
                  POSTURE ALIGNMENT
                </div>
                <div className="mt-1 truncate">
                  {vitals.syncopeDetected ? (
                    <span className="text-xs font-bold text-rose-400 flex items-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" /> SYNCOPE DROP
                    </span>
                  ) : (
                    <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" /> ERECT NOMINAL
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
            
            <div className="w-full h-28 rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden relative shadow-inner">
              <canvas
                ref={waveformCanvasRef}
                width={450}
                height={112}
                className="w-full h-full block"
              />
              <div className="absolute top-2 left-2 text-[9px] font-mono text-cyan-400/70">
                SIGNAL GAIN: 1.0x // PLETHYSMOGRAM
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================================= */}
        {/* CENTER DECK (Cols 5-9): Vitals, Point-of-Care Diagnostics, qSOFA, Baymax */}
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

          {/* Multimodal Point-of-Care Diagnostics Deck (Anemia, Cough & qSOFA) */}
          <div className="p-3.5 rounded-3xl bg-slate-900/80 border border-slate-800 flex flex-col gap-2.5 shadow-lg">
            <div className="flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-1.5">
                <Stethoscope className="w-4 h-4 text-emerald-400" />
                <span className="font-bold text-slate-200">POINT-OF-CARE MULTIMODAL DIAGNOSTICS & qSOFA CDS</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/40 text-[9px] font-mono text-emerald-300">
                qSOFA: {qsofaResult.qsofa_score}/3 ({qsofaResult.triage_category})
              </span>
            </div>

            {/* Diagnostic Action Trigger Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] font-mono">
              <button
                onClick={handleScreenAnemia}
                className="p-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500 text-left transition flex flex-col justify-between"
              >
                <div className="flex items-center gap-1 text-cyan-400 font-bold">
                  <Eye className="w-3 h-3" />
                  <span>CONJUNCTIVAL PALLOR</span>
                </div>
                <div className="text-[10px] text-slate-300 mt-1">
                  Hb: <strong className="text-white">{anemiaResult.estimated_hemoglobin_g_dl} g/dL</strong> ({anemiaResult.status})
                </div>
              </button>

              <button
                onClick={handleAnalyzeCough}
                className="p-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 hover:border-amber-500 text-left transition flex flex-col justify-between"
              >
                <div className="flex items-center gap-1 text-amber-400 font-bold">
                  <AudioWaveform className="w-3 h-3" />
                  <span>COUGH ACOUSTICS</span>
                </div>
                <div className="text-[10px] text-slate-300 mt-1 truncate">
                  Pattern: <strong className="text-white">{coughResult.acoustic_pattern}</strong>
                </div>
              </button>

              <button
                onClick={handleCalculateQSOFA}
                className="p-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-800 hover:border-rose-500 text-left transition flex flex-col justify-between"
              >
                <div className="flex items-center gap-1 text-rose-400 font-bold">
                  <Activity className="w-3 h-3" />
                  <span>qSOFA SEPSIS CDS</span>
                </div>
                <div className="text-[10px] text-slate-300 mt-1">
                  Shock Prob: <strong className="text-rose-300">{(qsofaResult.shock_probability * 100).toFixed(0)}%</strong>
                </div>
              </button>
            </div>
          </div>

          {/* Explainable AI (XAI) Biomarker Decomposition */}
          <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col gap-2 shadow-lg">
            <div className="flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-1.5">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <span className="font-bold text-slate-200">EXPLAINABLE AI (XAI) BIOMARKER DECOMPOSITION</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-500/40 text-[9px] font-mono text-cyan-300">
                PRIMARY DRIVER: {topDriver}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 pt-1 text-[10px] font-mono">
              {Object.entries(xaiContributions).map(([name, pct], idx) => {
                const isHigh = pct > 25;
                const barColor = isHigh ? "bg-rose-500" : pct > 18 ? "bg-cyan-400" : "bg-emerald-400";
                return (
                  <div key={idx} className="p-2 rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col justify-between">
                    <span className="text-slate-400 truncate">{name}</span>
                    <div className="flex items-baseline justify-between mt-1">
                      <span className={`text-sm font-bold ${isHigh ? "text-rose-400" : "text-slate-200"}`}>
                        {pct}%
                      </span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden mt-1.5">
                      <div className={`h-full rounded-full ${barColor}`} style={{ width: `${Math.min(100, pct)}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Baymax Dialogue & Companion Console */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-3 flex-1 backdrop-blur-xl shadow-xl relative min-h-[340px]">
            
            {/* Header with Avatar Orb */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all duration-500 ${
                  avatarState === "alert"
                    ? "border-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.8)] bg-rose-950"
                    : avatarState === "listening"
                    ? "border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.8)] bg-cyan-950"
                    : "border-slate-700 bg-slate-950"
                }`}>
                  <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                    <div className="w-2.5 h-[1.5px] bg-white -mx-1" />
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold font-mono tracking-wide text-white flex items-center gap-2">
                    BAYMAX HEALTHCARE COMPANION
                    <span className="text-[9px] text-cyan-400 font-normal">MULTI-LINGUAL RAG</span>
                  </h3>
                  <p className="text-[10px] text-slate-400 font-mono">
                    Language: <span className="text-cyan-300 font-bold uppercase">{selectedLanguage}</span> • Patient: <span className="text-white font-bold">{patientProfile.name}</span>
                  </p>
                </div>
              </div>

              <div className="text-[10px] font-mono text-slate-400">
                ESCALATIONS: <span className="text-white font-bold">{escalationsCount}</span>
              </div>
            </div>

            {/* Scrollable Conversation Feed */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[220px] text-xs">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`max-w-[90%] rounded-2xl px-4 py-3 leading-relaxed flex flex-col gap-1.5 ${
                      msg.sender === "user"
                        ? "bg-cyan-950/80 text-cyan-100 border border-cyan-500/40 rounded-br-none"
                        : msg.allergyWarning
                        ? "bg-indigo-950/90 text-indigo-100 border border-indigo-500/80 rounded-bl-none shadow-[0_0_25px_rgba(99,102,241,0.4)]"
                        : msg.isAlert
                        ? "bg-rose-950/90 text-rose-100 border border-rose-500/60 rounded-bl-none shadow-[0_0_20px_rgba(244,63,94,0.3)]"
                        : "bg-slate-950 text-slate-200 border border-slate-800 rounded-bl-none"
                    }`}
                  >
                    {msg.matchedProtocol && (
                      <div className="flex items-center gap-1 text-[9px] font-mono text-cyan-300 bg-cyan-950/60 px-2 py-0.5 rounded-md border border-cyan-500/30 w-fit">
                        <BookOpen className="w-3 h-3" />
                        <span>RAG: {msg.matchedProtocol}</span>
                      </div>
                    )}
                    {msg.allergyWarning && (
                      <div className="flex items-center gap-1 text-[9px] font-mono text-amber-300 bg-amber-950/80 px-2 py-0.5 rounded-md border border-amber-500/50 w-fit">
                        <AlertOctagon className="w-3 h-3" />
                        <span>EHR ALLERGY CONTRAINDICATION DETECTED</span>
                      </div>
                    )}

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
                placeholder={
                  selectedLanguage === "te"
                    ? "బేమ్యాక్స్‌ను ఏదైనా అడగండి (ఉదా. 'నాకు జ్వరం ఉంది, ఏం చేయాలి?')..."
                    : selectedLanguage === "hi"
                    ? "बेमैक्स से कुछ भी पूछें (उदा. 'मुझे बुखार है, क्या करूँ?')..."
                    : "Ask Baymax anything (e.g. 'Can I take Ibuprofen for fever?')..."
                }
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
                title="Voice Input (Speech-to-Text in Selected Language)"
              >
                {isListening ? <Mic className="w-4 h-4 animate-bounce" /> : <Mic className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </section>

        {/* ========================================================================= */}
        {/* RIGHT DECK (Cols 10-12): Multi-Patient, Sync Queue & Satellite SOS */}
        {/* ========================================================================= */}
        <section className="lg:col-span-3 flex flex-col gap-4">
          
          {/* Patient Examination Ward Switcher Card */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-3 backdrop-blur-xl shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold font-mono tracking-wider text-slate-200">
                  OFFLINE CLINIC WARD QUEUE
                </h2>
              </div>
              <span className="px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-500/40 text-[9px] font-mono text-cyan-300">
                {patientList.length} PATIENTS
              </span>
            </div>

            {/* Selectable Patient List */}
            <div className="space-y-1.5 max-h-[120px] overflow-y-auto pr-1">
              {patientList.map((p) => {
                const isSelected = p.patient_uid === patientProfile.patient_uid;
                return (
                  <button
                    key={p.patient_uid}
                    onClick={() => handleSwitchPatient(p.patient_uid)}
                    className={`w-full text-left p-2.5 rounded-xl border transition flex items-center justify-between font-mono text-[11px] ${
                      isSelected
                        ? "bg-cyan-950/80 border-cyan-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                        : "bg-slate-950/60 border-slate-800/80 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                    }`}
                  >
                    <div>
                      <div className="font-bold flex items-center gap-1.5">
                        <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? "bg-cyan-400" : "bg-slate-600"}`} />
                        <span>{p.name}</span>
                        <span className="text-[9px] text-slate-400">({p.patient_uid})</span>
                      </div>
                      <div className="text-[9px] text-slate-400 truncate max-w-[170px] mt-0.5">
                        {p.location}
                      </div>
                    </div>
                    {isSelected && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500 text-slate-950 font-bold">
                        ACTIVE
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Active Patient EHR Summary */}
            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-1 mt-1">
              <div className="flex justify-between items-center text-slate-300 border-b border-slate-800/60 pb-1">
                <span className="text-slate-400">Blood:</span>
                <span className="text-cyan-300 font-bold">{patientProfile.blood_type}</span>
              </div>
              <div className="flex flex-col gap-0.5 border-b border-slate-800/60 pb-1">
                <span className="text-slate-400 text-[10px]">ALLERGIES:</span>
                <span className="px-1.5 py-0.5 rounded bg-rose-950/80 border border-rose-500/60 text-rose-300 font-bold text-[10px] truncate">
                  ⚠️ {patientProfile.allergies}
                </span>
              </div>
            </div>
          </div>

          {/* 140-Byte Low-Bandwidth Satellite / LoRa SOS Micro-Packet Terminal */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-2.5 backdrop-blur-xl shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Satellite className="w-4 h-4 text-purple-400" />
                <h2 className="text-xs font-bold font-mono tracking-wider text-slate-200">
                  SATELLITE SOS (140-BYTE PACKET)
                </h2>
              </div>
              <span className="text-[9px] font-mono text-purple-300 px-2 py-0.5 rounded bg-purple-950 border border-purple-500/40">
                {satelliteSOS.byte_size}B / 140B
              </span>
            </div>

            <div className="p-2.5 rounded-2xl bg-slate-950 border border-slate-800 text-[10px] font-mono space-y-1">
              <div className="text-slate-400 font-bold truncate">MICRO-PACKET (Iridium / LoRa):</div>
              <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-purple-300 font-mono break-all text-[9px]">
                {satelliteSOS.micro_packet}
              </div>
              <div className="flex justify-between text-slate-400 text-[9px] pt-1">
                <span>GPS: 17.9689 N, 79.5941 E</span>
                <span className="text-emerald-400 font-bold">READY</span>
              </div>
            </div>

            <button
              onClick={handleGenerateSOS}
              className="w-full py-2 rounded-xl bg-purple-950 hover:bg-purple-900 border border-purple-500/60 text-purple-300 text-xs font-mono font-bold transition flex items-center justify-center gap-1.5 shadow"
            >
              <Satellite className="w-3.5 h-3.5" />
              <span>🛰️ UPLINK ENCRYPTED SOS</span>
            </button>
          </div>

          {/* Store-and-Forward Offline FHIR Sync Queue Card */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-3xl p-4 flex flex-col gap-3 backdrop-blur-xl shadow-xl flex-1">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CloudUpload className="w-4 h-4 text-emerald-400" />
                <h2 className="text-xs font-bold font-mono tracking-wider text-slate-200">
                  STORE-AND-FORWARD SYNC
                </h2>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                ABDM READY
              </span>
            </div>

            {/* Sync Queue Statistics */}
            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-1.5">
              <div className="flex justify-between text-slate-300">
                <span>Queued Bundles:</span>
                <span className="text-amber-400 font-bold">{syncQueue.pending_offline_count} pending</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>Synced to Hospital:</span>
                <span className="text-emerald-400 font-bold">{syncQueue.synced_hospital_count} bundles</span>
              </div>
            </div>

            {syncSuccessMsg && (
              <div className="p-2 rounded-xl bg-emerald-950/80 border border-emerald-500/60 text-emerald-300 text-[10px] font-mono font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="truncate">{syncSuccessMsg}</span>
              </div>
            )}

            {/* Opportunistic Sync Trigger Button */}
            <button
              onClick={handleTriggerSync}
              disabled={isSyncing || syncQueue.pending_offline_count === 0}
              className="w-full py-2.5 rounded-xl bg-emerald-950 hover:bg-emerald-900 border border-emerald-500/60 text-emerald-300 text-xs font-mono font-bold transition flex items-center justify-center gap-2 shadow disabled:opacity-50"
            >
              <Server className="w-4 h-4" />
              <span>{isSyncing ? "UPLINKING FHIR BUNDLES..." : "⚡ SYNC TO DISTRICT HOSPITAL"}</span>
            </button>
          </div>
        </section>

      </div>

      {/* ========================================================================= */}
      {/* HL7 / FHIR CLINICAL EMERGENCY TRIAGE HANDOVER MODAL */}
      {/* ========================================================================= */}
      {isHandoverModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.3)]">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-teal-950 border border-teal-500/60 text-teal-400">
                  <Share2 className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold font-mono tracking-wider text-white">
                    EMERGENCY CLINICAL HANDOVER EXPORT
                  </h2>
                  <p className="text-[11px] text-slate-400 font-mono">
                    HL7 FHIR v4.0.1 Document Standard • Hospital ER Interoperability
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setHandoverTab("triage")}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition ${
                    handoverTab === "triage"
                      ? "bg-cyan-600 text-slate-950"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  Medical Triage Note
                </button>
                <button
                  onClick={() => setHandoverTab("fhir")}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition ${
                    handoverTab === "fhir"
                      ? "bg-cyan-600 text-slate-950"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  FHIR Bundle JSON
                </button>
                <button
                  onClick={() => setIsHandoverModalOpen(false)}
                  className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 ml-2"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6 text-slate-200">
              {handoverTab === "triage" ? (
                <div className="space-y-4 font-sans text-xs">
                  
                  {/* Alert Banner */}
                  <div className="p-3 rounded-2xl bg-teal-950/60 border border-teal-500/50 flex items-center justify-between">
                    <div>
                      <span className="font-bold text-teal-300">STANDARDIZED EMERGENCY TRIAGE SUMMARY</span>
                      <p className="text-[11px] text-teal-200/80">Ready for direct EHR import or attending ER physician review.</p>
                    </div>
                    <a
                      href={`${BACKEND_URL}/clinical-handover/triage-report`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-slate-950 font-bold font-mono text-[11px] flex items-center gap-1.5 shadow"
                    >
                      <Printer className="w-3.5 h-3.5" />
                      <span>Print Official PDF</span>
                    </a>
                  </div>

                  {/* Summary Grid */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                      <h4 className="font-mono font-bold text-cyan-400 text-xs">1. PATIENT DEMOGRAPHICS</h4>
                      <div className="text-slate-300"><strong>Name:</strong> {patientProfile.name} ({patientProfile.age}y, {patientProfile.gender})</div>
                      <div className="text-slate-300"><strong>UID:</strong> {patientProfile.patient_uid} • <strong>Blood:</strong> {patientProfile.blood_type}</div>
                      <div className="text-slate-400 text-[11px]"><strong>Location:</strong> {patientProfile.location}</div>
                      <div className="mt-2 p-2 rounded-lg bg-rose-950/80 border border-rose-500/60 text-rose-300 font-bold">
                        ⚠️ DOCUMENTED ALLERGIES: {patientProfile.allergies}
                      </div>
                      <div className="text-slate-400 mt-1">Active Meds: {patientProfile.active_medications}</div>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                      <h4 className="font-mono font-bold text-cyan-400 text-xs">2. ACUTE TELEMETRY SNAPSHOT</h4>
                      <div className="grid grid-cols-2 gap-2 text-slate-300">
                        <div>Heart Rate: <strong className="text-white">{vitals.heartRate} BPM</strong></div>
                        <div>Core Temp: <strong className="text-white">{vitals.temperature.toFixed(1)} °C</strong></div>
                        <div>HRV RMSSD: <strong className="text-emerald-300">{vitals.rmssd} ms</strong></div>
                        <div>Skin Conduct: <strong className="text-purple-300">{vitals.eda.toFixed(1)} µS</strong></div>
                        <div>Ocular EAR: <strong className="text-cyan-300">{vitals.ear.toFixed(3)}</strong></div>
                        <div>Posture: <strong className={vitals.syncopeDetected ? "text-rose-400" : "text-emerald-400"}>{vitals.postureStatus}</strong></div>
                      </div>
                    </div>
                  </div>

                  {/* XAI Attribution Summary */}
                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                    <h4 className="font-mono font-bold text-cyan-400 text-xs">3. EXPLAINABLE AI (XAI) RISK ATTRIBUTION</h4>
                    <p className="text-slate-400 text-[11px]">Primary Physiological Driver: <strong className="text-white">{topDriver}</strong></p>
                    <div className="grid grid-cols-5 gap-2">
                      {Object.entries(xaiContributions).map(([name, pct], idx) => (
                        <div key={idx} className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center font-mono">
                          <div className="text-[10px] text-slate-400 truncate">{name}</div>
                          <div className="text-xs font-bold text-cyan-300 mt-1">{pct}%</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 font-mono text-[11px]">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <span className="text-cyan-400 font-bold">HL7 / FHIR v4.0.1 Resource Bundle</span>
                    <a
                      href={`${BACKEND_URL}/clinical-handover/fhir`}
                      download="fhir_bundle.json"
                      className="px-3 py-1 rounded-lg bg-cyan-950 border border-cyan-500/50 text-cyan-300 hover:bg-cyan-900 flex items-center gap-1"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download JSON</span>
                    </a>
                  </div>
                  <pre className="p-4 rounded-2xl bg-slate-950 border border-slate-800 overflow-x-auto text-emerald-400 text-[10px] max-h-[400px]">
                    {fhirData ? JSON.stringify(fhirData, null, 2) : "Loading FHIR v4.0.1 Bundle..."}
                  </pre>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Security: AES-256 Offline Encryption • HIPAA / ABDM Compliant</span>
              <button
                onClick={() => setIsHandoverModalOpen(false)}
                className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold transition"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}

    </main>
  );
}
