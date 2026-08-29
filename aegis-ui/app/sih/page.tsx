"use client";

import { useState } from "react";

type Scenario = "normal" | "disaster";
type Result = {
  risk_score: string;
  escalated: boolean;
  clinical_notice: string;
  environmental_assessment?: {
    level: string;
    heat_index_c?: number;
    hazards: string[];
    recommendations: string[];
  };
};

const scenarios = {
  normal: {
    heart_rate: 74,
    temperature: 36.8,
    environment: { ambient_temperature_c: 29, humidity_percent: 55, aqi: 72, flood_warning: false },
  },
  disaster: {
    heart_rate: 118,
    temperature: 38.4,
    environment: { ambient_temperature_c: 43, humidity_percent: 70, aqi: 330, flood_warning: true },
  },
};

function offlineFallback(scenario: Scenario): Result {
  if (scenario === "normal") {
    return {
      risk_score: "Normal",
      escalated: false,
      clinical_notice: "Browser-local fallback active — wellness decision support only.",
      environmental_assessment: { level: "NORMAL", hazards: [], recommendations: ["No environmental hazard detected."] },
    };
  }
  return {
    risk_score: "High",
    escalated: true,
    clinical_notice: "Browser-local fallback active — wellness decision support only.",
    environmental_assessment: {
      level: "HIGH",
      heat_index_c: 61.8,
      hazards: ["EXTREME_HEAT_STRESS", "SEVERE_AIR_QUALITY", "FLOOD_DISRUPTION"],
      recommendations: ["Move to cooling now.", "Avoid outdoor exertion.", "Keep medicines and drinking water ready."],
    },
  };
}

export default function SIHDemoPage() {
  const [result, setResult] = useState<Result>(offlineFallback("normal"));
  const [source, setSource] = useState("Browser-local preview");
  const [sharingConsent, setSharingConsent] = useState(false);
  const [loading, setLoading] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_AEGIS_BACKEND_URL || "http://127.0.0.1:8000";
  const token = process.env.NEXT_PUBLIC_AEGIS_TOKEN;

  async function runScenario(scenario: Scenario) {
    setLoading(true);
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["X-AEGIS-Token"] = token;
    try {
      const response = await fetch(`${backendUrl}/ingest-telemetry`, {
        method: "POST",
        headers,
        body: JSON.stringify({ ...scenarios[scenario], consent_to_share_emergency_alert: sharingConsent }),
      });
      if (!response.ok) throw new Error("Local AEGIS endpoint is unavailable");
      setResult(await response.json());
      setSource("Local AEGIS runtime — no cloud required");
    } catch {
      setResult(offlineFallback(scenario));
      setSource("Browser-local offline fallback — backend unreachable");
    } finally {
      setLoading(false);
    }
  }

  const assessment = result.environmental_assessment;
  const highRisk = result.risk_score.toLowerCase().includes("high");

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold tracking-[0.3em] text-cyan-300">SIH26181 · OFFLINE FIRST</p>
            <h1 className="mt-2 text-4xl font-bold">AEGIS Personal Health Companion</h1>
            <p className="mt-2 max-w-2xl text-slate-400">Early warning for heat, pollution, flood disruption and physiological strain — kept on the user’s device.</p>
          </div>
          <span className={`rounded-full px-4 py-2 text-sm font-bold ${highRisk ? "bg-rose-500/20 text-rose-300" : "bg-emerald-500/20 text-emerald-300"}`}>
            {highRisk ? "HIGH-RISK ALERT" : "STATUS: NORMAL"}
          </span>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><p className="text-sm text-slate-400">Risk assessment</p><p className="mt-2 text-3xl font-bold">{result.risk_score}</p><p className="mt-2 text-sm text-slate-400">{source}</p></article>
          <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><p className="text-sm text-slate-400">Environmental level</p><p className="mt-2 text-3xl font-bold">{assessment?.level ?? "NORMAL"}</p><p className="mt-2 text-sm text-slate-400">Heat index: {assessment?.heat_index_c ?? "—"} °C</p></article>
          <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5"><p className="text-sm text-slate-400">Privacy state</p><p className="mt-2 text-3xl font-bold text-emerald-300">LOCAL</p><p className="mt-2 text-sm text-slate-400">Encrypted records · sharing requires consent</p></article>
        </section>

        <section className="mt-5 grid gap-5 md:grid-cols-[1.2fr_0.8fr]">
          <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-bold">Judge demo controls</h2>
            <p className="mt-2 text-sm text-slate-400">Start normal, then trigger the disaster scenario. This is the full SIH story in two clicks.</p>
            <div className="mt-5 flex flex-wrap gap-3">
              <button onClick={() => runScenario("normal")} disabled={loading} className="rounded-lg bg-emerald-500 px-4 py-3 font-bold text-slate-950 disabled:opacity-60">1. Normal check</button>
              <button onClick={() => runScenario("disaster")} disabled={loading} className="rounded-lg bg-rose-500 px-4 py-3 font-bold text-white disabled:opacity-60">2. Heat + AQI + flood</button>
            </div>
            <label className="mt-5 flex items-center gap-3 rounded-lg bg-slate-800 p-3 text-sm">
              <input type="checkbox" checked={sharingConsent} onChange={(event) => setSharingConsent(event.target.checked)} />
              I consent to share an emergency alert with my configured contact.
            </label>
            <p className="mt-3 text-xs text-slate-500">{result.clinical_notice}</p>
          </article>

          <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-bold">Actionable alert</h2>
            <div className="mt-4 space-y-2">
              {(assessment?.hazards.length ? assessment.hazards : ["No active hazards"]).map((hazard) => <p key={hazard} className="rounded-md bg-slate-800 px-3 py-2 text-sm font-semibold">{hazard}</p>)}
            </div>
            <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate-300">
              {(assessment?.recommendations ?? []).map((recommendation) => <li key={recommendation}>{recommendation}</li>)}
            </ul>
            {result.escalated && <p className="mt-4 rounded-md bg-rose-500/15 p-3 text-sm text-rose-200">Emergency mode is active. Sharing remains opt-in.</p>}
          </article>
        </section>
      </div>
    </main>
  );
}
