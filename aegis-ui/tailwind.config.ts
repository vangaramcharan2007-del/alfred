import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080c14",
        foreground: "#f8fafc",
        clinical: {
          dark: "#05080f",
          card: "#0d1322",
          border: "#1e293b",
          cyan: "#06b6d4",
          emerald: "#10b981",
          rose: "#f43f5e",
          amber: "#f59e0b",
          purple: "#8b5cf6"
        },
      },
      animation: {
        "pulse-fast": "pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-cyan": "glowCyan 2s ease-in-out infinite alternate",
        "glow-rose": "glowRose 1.5s ease-in-out infinite alternate",
      },
      keyframes: {
        glowCyan: {
          "0%": { boxShadow: "0 0 10px rgba(6, 182, 212, 0.3)" },
          "100%": { boxShadow: "0 0 25px rgba(6, 182, 212, 0.7)" },
        },
        glowRose: {
          "0%": { boxShadow: "0 0 10px rgba(244, 63, 94, 0.4)" },
          "100%": { boxShadow: "0 0 30px rgba(244, 63, 94, 0.9)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
