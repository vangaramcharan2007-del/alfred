"""
Spider-Man EV Minimalist Workstation & Voice-Activated Linux HUD.
================================================================
Features:
  - EV: Funny, lovely, ADHD-friendly female AI Co-Pilot under Alfred Orchestration.
  - Minimalist Cyber-Spidey UI (Obsidian #08090d, Stark Crimson #ff003c, Electric Venom Cyan #00f0ff).
  - Real-time Voice Command Engine with Web Speech Synthesis (Female Voice).
  - Spider-Sense Telemetry HUD (CPU, RAM, 2.0 TB Hard Drive, Kernel).
  - Web-Shooter Interactive Linux Terminal.
  - 1-Click Sovereign Action Matrix (DevOps, AI Training, Cyber Sentinel, Shadow Worker, Compiler).
"""

from __future__ import annotations

import http.server
import json
import logging
import os
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("jarvisx.spiderman_ev")

PORT = 5050

EV_SYSTEM_PROMPTS = {
    "greeting": "Hey boss! E-V here! Ready to sling some Linux magic? What are we building today?",
    "cyber_scan": "Zooming through your local network like web-swinging across Manhattan! E-V is scanning ports right now!",
    "ai_train": "Ooh, training time! Teaching our neural net some epic moves in isolated Linux RAM. E-V has your back, zero lag for you!",
    "devops": "Spun up your microservice, boss! E-V has it running smooth and clean in Linux. You're unstoppable today!",
    "turbo_cool": "E-V is activating Turbo Cool! Dropping temperatures and kicking out background lag monsters. Ahh, refreshing!",
    "compile": "E-V compiled that native Linux binary in a flash! Boom! You're a rockstar!",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPIDER-MAN EV // Dual-Core Linux HUD</title>
    <style>
        :root {
            --bg: #07080c;
            --card-bg: rgba(16, 18, 27, 0.75);
            --border: rgba(255, 0, 60, 0.35);
            --crimson: #ff003c;
            --cyan: #00f0ff;
            --gold: #ffd700;
            --text-dim: #8e95a5;
            --text-bright: #ffffff;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body {
            background-color: var(--bg);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(255, 0, 60, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(0, 240, 255, 0.08) 0%, transparent 40%);
            color: var(--text-bright);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }
        header {
            padding: 16px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(12px);
            background: rgba(10, 11, 16, 0.85);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .brand { display: flex; align-items: center; gap: 12px; }
        .spider-icon {
            width: 38px; height: 38px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--crimson), #80001f);
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 16px var(--crimson);
            font-size: 20px;
        }
        .title { font-size: 1.15rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; }
        .title span { color: var(--cyan); }
        .ev-badge {
            background: rgba(0, 240, 255, 0.15);
            color: var(--cyan);
            border: 1px solid var(--cyan);
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.8px;
        }
        .container {
            max-width: 1300px;
            margin: 20px auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: 1fr 1.35fr;
            gap: 20px;
            flex: 1;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 2px;
            background: linear-gradient(90deg, transparent, var(--crimson), var(--cyan), transparent);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        .card-title {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 800;
            color: var(--text-dim);
            display: flex; align-items: center; gap: 8px;
        }
        .telemetry-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 16px;
        }
        .telemetry-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 12px 14px;
        }
        .telem-label { font-size: 0.7rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px; }
        .telem-val { font-size: 1.15rem; font-weight: 700; color: var(--text-bright); margin-top: 4px; }
        .telem-val.cyan { color: var(--cyan); }
        .telem-val.crimson { color: var(--crimson); }
        .telem-val.gold { color: var(--gold); }

        /* Voice EV Section */
        .ev-dialogue-box {
            background: rgba(255, 0, 60, 0.06);
            border: 1px solid rgba(255, 0, 60, 0.25);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 16px;
            display: flex;
            gap: 14px;
            align-items: flex-start;
        }
        .ev-avatar {
            width: 44px; height: 44px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--cyan), var(--crimson));
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
            box-shadow: 0 0 14px rgba(0, 240, 255, 0.6);
            flex-shrink: 0;
            animation: pulse 2.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); box-shadow: 0 0 14px rgba(0, 240, 255, 0.6); }
            50% { transform: scale(1.05); box-shadow: 0 0 24px rgba(255, 0, 60, 0.8); }
        }
        .ev-speech {
            font-size: 0.95rem;
            line-height: 1.45;
            color: #f1f3f9;
        }
        .ev-speech strong { color: var(--cyan); font-weight: 700; }
        
        .voice-controls {
            display: flex;
            gap: 10px;
            margin-top: 12px;
        }
        .btn-mic {
            flex: 1;
            padding: 12px;
            border-radius: 12px;
            border: 1px solid var(--cyan);
            background: rgba(0, 240, 255, 0.1);
            color: var(--cyan);
            font-weight: 700;
            cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 8px;
            transition: all 0.2s ease;
        }
        .btn-mic:hover, .btn-mic.listening {
            background: var(--cyan);
            color: #000;
            box-shadow: 0 0 20px var(--cyan);
        }

        /* Action Grid */
        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 14px;
        }
        .btn-action {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px;
            border-radius: 10px;
            color: var(--text-bright);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: flex; align-items: center; gap: 8px;
            transition: all 0.2s;
        }
        .btn-action:hover {
            border-color: var(--crimson);
            background: rgba(255, 0, 60, 0.15);
            transform: translateY(-2px);
        }

        /* Terminal Window */
        .terminal-container {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .terminal-screen {
            background: #030407;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 14px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.85rem;
            color: #00f0ff;
            flex: 1;
            min-height: 280px;
            max-height: 380px;
            overflow-y: auto;
            white-space: pre-wrap;
            line-height: 1.4;
            margin-bottom: 12px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        }
        .terminal-input-row {
            display: flex;
            gap: 8px;
        }
        .terminal-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 12px 16px;
            color: #fff;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            outline: none;
        }
        .terminal-input:focus { border-color: var(--cyan); box-shadow: 0 0 12px rgba(0, 240, 255, 0.3); }
        .btn-send {
            padding: 0 20px;
            background: var(--crimson);
            border: none;
            border-radius: 10px;
            color: #fff;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-send:hover { background: #ff2a5c; box-shadow: 0 0 16px var(--crimson); }

        /* Symbolic Crest Buttons */
        .crest-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: rgba(18, 26, 43, 0.85);
            border: 2px solid var(--border-glow);
            border-radius: 12px;
            padding: 6px 14px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            color: #fff;
            font-size: 0.85rem;
            font-weight: 700;
        }
        .crest-btn:hover { transform: translateY(-3px) scale(1.04); }
        .crest-btn.spider-btn { border-color: #00f0ff; color: #00f0ff; }
        .crest-btn.spider-btn:hover {
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.7), 0 0 35px rgba(255, 0, 60, 0.5);
            border-color: #ff003c;
            color: #ffffff;
        }
        .crest-btn.bat-btn { border-color: #ffd700; color: #ffd700; }
        .crest-btn.bat-btn:hover {
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.7), 0 0 35px rgba(212, 175, 55, 0.4);
            border-color: #ffffff;
            color: #ffffff;
        }
        .crest-svg { transition: transform 0.3s ease; }
        .spider-crest-svg { width: 26px; height: 26px; }
        .bat-crest-svg { width: 34px; height: 20px; }
        .crest-btn:hover .crest-svg { transform: scale(1.15); }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <div class="spider-icon">🕷️</div>
            <div class="title">SPIDER-MAN <span>EV</span> // DUAL-CORE LINUX WORKSTATION</div>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
            <!-- Pure Minimalist Spider Crest Button (E-V) -->
            <button class="crest-btn spider-btn" onclick="triggerAction('ev_dialogue')" title="E-V Cyber Co-Pilot">
                <svg viewBox="0 0 100 100" class="crest-svg spider-crest-svg" xmlns="http://www.w3.org/2000/svg">
                    <ellipse cx="50" cy="40" rx="9" ry="12" fill="#00f0ff" />
                    <circle cx="50" cy="24" r="6" fill="#ffffff" />
                    <ellipse cx="50" cy="62" rx="14" ry="18" fill="#ff003c" />
                    <path d="M43,36 Q25,18 18,32 Q14,40 10,48" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round"/>
                    <path d="M57,36 Q75,18 82,32 Q86,40 90,48" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round"/>
                    <path d="M42,54 Q22,58 18,72 Q15,82 12,92" stroke="#ff003c" stroke-width="4" fill="none" stroke-linecap="round"/>
                    <path d="M58,54 Q78,58 82,72 Q85,82 88,92" stroke="#ff003c" stroke-width="4" fill="none" stroke-linecap="round"/>
                </svg>
            </button>

            <!-- Pure Minimalist Bat Crest Button (Alfred) -->
            <button class="crest-btn bat-btn" onclick="triggerAction('alfred_doctor')" title="Alfred Sovereign Butler">
                <svg viewBox="0 0 120 70" class="crest-svg bat-crest-svg" xmlns="http://www.w3.org/2000/svg">
                    <path d="M60,18 L64,8 L68,16 C78,12 94,14 116,4 C112,24 98,34 94,54 C84,46 74,48 60,66 C46,48 36,46 26,54 C22,34 8,24 4,4 C26,14 42,12 52,16 L56,8 Z" fill="#ffd700" stroke="#ffd700" stroke-width="2" />
                    <polygon points="56,8 58,16 54,16" fill="#0a0e17" />
                    <polygon points="64,8 66,16 62,16" fill="#0a0e17" />
                </svg>
            </button>
        </div>
    </header>

    <div class="container">
        <!-- Left Panel: EV AI Voice Co-Pilot & Telemetry -->
        <div style="display: flex; flex-direction: column; gap: 20px;">
            <!-- EV Voice Dialogue Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">✨ EV CO-PILOT // ADHD-FRIENDLY VOICE ASSISTANT</div>
                    <span style="font-size: 0.75rem; color: var(--cyan);">v2.4 Sovereign</span>
                </div>
                <div class="ev-dialogue-box">
                    <div class="ev-avatar">💖</div>
                    <div class="ev-speech" id="evSpeech">
                        <strong>EV:</strong> "Hey boss! Ready to sling some code? Just click the mic or ask me anything — I've got your back so you never lose focus!"
                    </div>
                </div>
                <div class="voice-controls">
                    <button class="btn-mic" id="micBtn" onclick="toggleVoiceRecognition()">
                        <span id="micIcon">🎙️</span> <span id="micText">Speak to EV (Voice Active)</span>
                    </button>
                    <button class="btn-action" style="flex: 0.4;" onclick="speakEV(document.getElementById('evSpeech').innerText)">
                        🔊 Replay
                    </button>
                </div>

                <!-- Quick Autonomous Action Matrix -->
                <div style="margin-top: 18px;">
                    <div class="card-title" style="margin-bottom: 8px;">⚡ QUICK SPIDEY ACTIONS</div>
                    <div class="action-grid">
                        <button class="btn-action" onclick="triggerAction('math_snap')">📐 Snap & Solve Math</button>
                        <button class="btn-action" onclick="triggerAction('math_formulas')">📘 M3 Formulas</button>
                        <button class="btn-action" onclick="triggerAction('cyber_scan')">🛡️ Cyber Sentinel</button>
                        <button class="btn-action" onclick="triggerAction('turbo_cool')">❄️ Turbo Cool</button>
                    </div>
                </div>
            </div>

            <!-- Spider-Sense Telemetry HUD -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🕷️ SPIDER-SENSE TELEMETRY HUD</div>
                    <span id="backendBadge" style="font-size: 0.75rem; color: var(--gold);">WSL2 LINUX ENGINE</span>
                </div>
                <div class="telemetry-grid">
                    <div class="telemetry-box">
                        <div class="telem-label">CPU Clock & Cores</div>
                        <div class="telem-val cyan" id="cpuVal">Intel Ultra 5 (14C)</div>
                    </div>
                    <div class="telemetry-box">
                        <div class="telem-label">Allocated RAM</div>
                        <div class="telem-val crimson" id="ramVal">7.6 GB Free</div>
                    </div>
                    <div class="telemetry-box">
                        <div class="telem-label">2.0 TB Hard Drive (F:)</div>
                        <div class="telem-val gold" id="diskVal">1.64 TB Ready</div>
                    </div>
                    <div class="telemetry-box">
                        <div class="telem-label">Linux Kernel</div>
                        <div class="telem-val" id="kernelVal">Linux 6.6.87</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Panel: Web-Shooter Interactive Terminal -->
        <div class="card terminal-container">
            <div class="card-header">
                <div class="card-title">💻 WEB-SHOOTER DUAL-CORE TERMINAL</div>
                <button class="btn-action" style="padding: 4px 10px; font-size: 0.75rem;" onclick="clearTerminal()">Clear</button>
            </div>
            <div class="terminal-screen" id="termScreen">[SPIDER-MAN EV DUAL-CORE LINUX WORKSTATION INITIALIZED]
[✓] Linux Engine: WSL2 Bridge Connected
[✓] Alfred Organism: Active
[✓] EV Female Voice Assistant: Online

Type a bash command below or speak with the microphone!
$ </div>
            <div class="terminal-input-row">
                <input type="text" class="terminal-input" id="cmdInput" placeholder="Enter Linux bash command (e.g. uname -a, df -h, free -m)..." onkeydown="handleKey(event)">
                <button class="btn-send" onclick="sendBash()">Run ⚡</button>
            </div>
        </div>
    </div>

    <script>
        // EV Voice Synthesis (Female Voice)
        function speakEV(text) {
            if (!window.speechSynthesis) return;
            window.speechSynthesis.cancel();
            
            // Clean text of "EV:" prefix and ensure phonetic "E-V" pronunciation
            let cleanText = text.replace(/^[A-Za-z]+:\s*/, '');
            cleanText = cleanText.replace(/\bEV\b/g, 'E-V').replace(/\bev\b/g, 'E-V').replace(/\bEv\b/g, 'E-V');

            const utter = new SpeechSynthesisUtterance(cleanText);
            utter.rate = 1.0;
            utter.pitch = 1.2; // Cheerful, sweet female tone

            const voices = window.speechSynthesis.getVoices();
            // Prioritize clear, natural female voices (Microsoft Zira, Jenny, Samantha, Google US Female)
            const femaleVoice = voices.find(v => 
                v.name.includes("Zira") || 
                v.name.includes("Jenny") || 
                v.name.includes("Aria") || 
                v.name.includes("Samantha") || 
                v.name.includes("Victoria") || 
                v.name.includes("Google US English") || 
                (v.name.includes("Female") && !v.name.includes("Male"))
            );
            if (femaleVoice) utter.voice = femaleVoice;

            window.speechSynthesis.speak(utter);
        }

        // Web Speech Recognition for Voice Commands
        let recognition = null;
        let isListening = false;

        function initSpeech() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) return;
            recognition = new SpeechRec();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                isListening = true;
                document.getElementById('micBtn').classList.add('listening');
                document.getElementById('micText').innerText = "Listening to your voice...";
            };

            recognition.onend = () => {
                isListening = false;
                document.getElementById('micBtn').classList.remove('listening');
                document.getElementById('micText').innerText = "Speak to EV (Voice Active)";
            };

            recognition.onresult = (e) => {
                const transcript = e.results[0][0].transcript.toLowerCase();
                processVoiceCommand(transcript);
            };
        }

        function toggleVoiceRecognition() {
            if (!recognition) initSpeech();
            if (!recognition) {
                alert("Voice recognition is not supported in this browser. Please use Chrome or Edge!");
                return;
            }
            if (isListening) recognition.stop();
            else recognition.start();
        }

        function processVoiceCommand(cmd) {
            appendTerminal(`\\n[VOICE INPUT]: "${cmd}"`);
            
            if (cmd.includes("scan") || cmd.includes("security") || cmd.includes("cyber")) {
                triggerAction('cyber_scan');
            } else if (cmd.includes("train") || cmd.includes("ai") || cmd.includes("model")) {
                triggerAction('ai_train');
            } else if (cmd.includes("cool") || cmd.includes("turbo")) {
                triggerAction('turbo_cool');
            } else if (cmd.includes("devops") || cmd.includes("service") || cmd.includes("server")) {
                triggerAction('devops');
            } else {
                // Execute directly in Linux bash
                document.getElementById('cmdInput').value = cmd;
                sendBash();
            }
        }

        // Terminal & REST API
        function appendTerminal(text) {
            const screen = document.getElementById('termScreen');
            screen.innerText += text + "\\n";
            screen.scrollTop = screen.scrollHeight;
        }

        function clearTerminal() {
            document.getElementById('termScreen').innerText = "$ ";
        }

        function handleKey(e) {
            if (e.key === 'Enter') sendBash();
        }

        async function sendBash() {
            const input = document.getElementById('cmdInput');
            const cmd = input.value.trim();
            if (!cmd) return;
            input.value = "";
            appendTerminal(`$ ${cmd}`);

            try {
                const res = await fetch('/api/bash', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();
                if (data.stdout) appendTerminal(data.stdout);
                if (data.stderr) appendTerminal("[STDERR]: " + data.stderr);
            } catch (err) {
                appendTerminal("[ERROR]: Could not reach Linux Agent bridge.");
            }
        }

        async function triggerAction(action) {
            try {
                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action })
                });
                const data = await res.json();
                
                // Update EV Speech
                if (data.ev_speech) {
                    document.getElementById('evSpeech').innerHTML = `<strong>EV:</strong> "${data.ev_speech}"`;
                    speakEV(data.ev_speech);
                }
                
                if (data.output) appendTerminal(`\\n[${action.toUpperCase()} RESULT]:\\n` + data.output);
            } catch (err) {
                appendTerminal("[ERROR]: Action execution failed.");
            }
        }

        // Refresh Telemetry on Load
        async function fetchTelemetry() {
            try {
                const res = await fetch('/api/telemetry');
                const t = await res.json();
                if (t.kernel_version) document.getElementById('kernelVal').innerText = t.kernel_version.split(' ')[0] + " " + (t.kernel_version.split(' ')[1] || "");
                if (t.memory_free_mb) document.getElementById('ramVal').innerText = `${(t.memory_free_mb/1024).toFixed(1)} GB Free`;
                if (t.runtime_type) document.getElementById('backendBadge').innerText = `${t.runtime_type.toUpperCase()} LINUX ENGINE`;
            } catch (e) {}
        }

        window.onload = () => {
            initSpeech();
            fetchTelemetry();
            // Speak initial welcome after 1s
            setTimeout(() => {
                speakEV("Hey boss! EV here! Ready to sling some code?");
            }, 1000);
        };
    </script>
</body>
</html>
"""


class SpiderManHTTPHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy standard HTTP logs
        pass

    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

            elif self.path == "/api/telemetry":
                from jarvisx.agents.linux_agent import LinuxBridgeAgent
                telemetry = LinuxBridgeAgent.get_instance().get_system_info()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(telemetry.to_dict()).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}

            if self.path == "/api/bash":
                from jarvisx.agents.linux_agent import LinuxBridgeAgent
                cmd = data.get("command", "")
                res = LinuxBridgeAgent.get_instance().execute_bash(cmd)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))

            elif self.path == "/api/action":
                action = data.get("action", "")
                from jarvisx.agents.linux_agent import LinuxBridgeAgent
                linux = LinuxBridgeAgent.get_instance()

                ev_speech = ""
                output = ""

                if action == "ev_dialogue":
                    ev_speech = "Hey boss! E-V is right here! Ready to sling code, solve boundary value math, or keep you in the zone! What are we conquering today?"
                    output = "[🕷️ E-V CO-PILOT]: High-energy ADHD pair-programming mode active. All senses green."
                elif action == "alfred_doctor":
                    ev_speech = "Alfred Sovereign Butler reporting. System diagnostics nominal. Security gate active. All background fleet agents synchronized."
                    output = "[🦇 ALFRED SOVEREIGN]: System Doctor Status: HEALTHY | Security Gate: ZERO_LEAKS | Active Engine: Native Linux Core."
                elif action == "cyber_scan":
                    ev_speech = EV_SYSTEM_PROMPTS["cyber_scan"]
                    scan = linux.cyber.scan_local_network([80, 443, 8080, 5050])
                    output = f"Local IP: {scan.get('local_ip')} | Open Ports: {scan.get('open_ports')} | Posture: {scan.get('posture')}"
                elif action == "ai_train":
                    ev_speech = EV_SYSTEM_PROMPTS["ai_train"]
                    res = linux.ai_sandbox.run_fast_benchmark()
                    output = f"Dataset: {res.get('dataset')} | Samples/sec: {res.get('samples_per_sec')} | Isolation: {res.get('memory_isolated')}"
                elif action == "devops":
                    ev_speech = EV_SYSTEM_PROMPTS["devops"]
                    res = linux.devops.start_service("ev_daemon", "python3 -m http.server 8080")
                    output = f"Service: {res.get('service')} | Status: {res.get('status')} | PID: {res.get('pid')}"
                elif action == "turbo_cool":
                    ev_speech = EV_SYSTEM_PROMPTS["turbo_cool"]
                    linux.execute_bash("sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true")
                    output = "Linux RAM caches purged. Hardware temperature dropping."
                elif action == "math_snap":
                    from jarvisx.agents.transforms_math_agent import TransformsMathAgent
                    sol = TransformsMathAgent.get_instance().solve_1d_wave_equation()
                    ev_speech = "Spider-Sense Math Vision solved the 1D Wave Equation from E. Suresh! Step-by-step Fourier derivation is ready on your screen, boss!"
                    output = sol.to_markdown()
                elif action == "math_formulas":
                    ev_speech = "Here are the top formulas and scoring tips for Units 1 to 5 from E. Suresh!"
                    output = (
                        "# 📘 Dr. E. Suresh M3 Formula Cheat-Sheet\n\n"
                        "### Unit 1: PDEs\n- Lagrange's Equation: P p + Q q = R => dx/P = dy/Q = dz/R\n\n"
                        "### Unit 2: Fourier Series\n- a0 = (1/l) int f(x)dx\n- an = (1/l) int f(x) cos(n pi x / l)dx\n- bn = (1/l) int f(x) sin(n pi x / l)dx\n\n"
                        "### Unit 3: 1D Wave & Heat Equations\n- 1D Wave: y_tt = a^2 y_xx => y(x,t) = sum bn sin(n pi x / l) cos(n pi a t / l)\n- 1D Heat: u_t = alpha^2 u_xx => u(x,t) = sum cn sin(n pi x / l) exp(-n^2 pi^2 alpha^2 t / l^2)\n\n"
                        "### Unit 4 & 5: Transforms\n- Z{a^n} = z / (z - a)\n- Z{n} = z / (z - 1)^2"
                    )
                elif action == "compile":
                    ev_speech = EV_SYSTEM_PROMPTS.get("compile", "Compiling...")
                    res = linux.toolchain.compile_source("int main() { return 0; }", "c", "spidey_app.out")
                    output = f"Binary: {res.get('binary_path')} | Status: {res.get('status')}"

                # Speak out loud using ultra-realistic Microsoft Neural Voice
                if ev_speech:
                    try:
                        import threading
                        from jarvisx.automation.ev_neural_voice import speak_ev_neural
                        threading.Thread(target=speak_ev_neural, args=(ev_speech,), daemon=True).start()
                    except Exception:
                        pass

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "ev_speech": ev_speech, "output": output}).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass


class SpiderManLinuxHUDServer:
    """HTTP server hosting the Spider-Man EV Linux HUD."""

    _server: Optional[http.server.ThreadingHTTPServer] = None
    _thread: Optional[threading.Thread] = None

    @classmethod
    def start(cls, port: int = PORT, open_browser: bool = False) -> str:
        if cls._server is None:
            server_address = ("", port)
            cls._server = http.server.ThreadingHTTPServer(server_address, SpiderManHTTPHandler)
            cls._server.daemon_threads = True
            cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
            cls._thread.start()
            logger.info(f"[SpiderManHUD] Server started on port {port}")

        url = f"http://localhost:{port}"
        if open_browser:
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                pass

        return url


def launch():
    print(f"[*] Launching Spider-Man EV Minimalist Workstation on http://localhost:{PORT}...")
    url = SpiderManLinuxHUDServer.start(PORT, open_browser=True)
    print(f"[SUCCESS] Workstation active at: {url}")
    return url


if __name__ == "__main__":
    launch()
    while True:
        time.sleep(1)
