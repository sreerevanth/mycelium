import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // MYCELIUM design system - bio-computational substrate palette
        mycelium: {
          void: "#020408",
          deep: "#050d12",
          dark: "#0a1a20",
          mid: "#0f2630",
          surface: "#132d38",
          border: "#1a3d4a",
          muted: "#2a5a6e",
          dim: "#3a7a94",
          subtle: "#4a9ab8",
          accent: "#5bbdd6",
          bright: "#7dd4e8",
          glow: "#a0e8f5",
          pulse: "#c8f5ff",
        },
        spore: {
          100: "#1a3320",
          200: "#2a5530",
          300: "#3a7740",
          400: "#4a9950",
          500: "#5abb60",
          600: "#7acd80",
          700: "#9adfa0",
          800: "#baf1c0",
        },
        extinction: {
          100: "#331a1a",
          200: "#552a2a",
          300: "#773a3a",
          400: "#994a4a",
          500: "#bb5a5a",
          600: "#cd7a7a",
          700: "#df9a9a",
          800: "#f1baba",
        },
        dominant: {
          100: "#33280a",
          200: "#55420a",
          300: "#775c0a",
          400: "#99760a",
          500: "#bb960a",
          600: "#cdaa2a",
          700: "#dfbf4a",
          800: "#f1d46a",
        },
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "'Fira Code'", "monospace"],
        display: ["'Space Mono'", "monospace"],
        sans: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "genome-spawn": "genome-spawn 0.6s ease-out forwards",
        "extinction": "extinction 1s ease-in forwards",
        "hyphae-grow": "hyphae-grow 2s ease-out forwards",
      },
      keyframes: {
        "genome-spawn": {
          "0%": { transform: "scale(0) rotate(-180deg)", opacity: "0" },
          "60%": { transform: "scale(1.2) rotate(10deg)", opacity: "0.8" },
          "100%": { transform: "scale(1) rotate(0deg)", opacity: "1" },
        },
        "extinction": {
          "0%": { transform: "scale(1)", opacity: "1", filter: "brightness(1)" },
          "50%": { transform: "scale(1.5)", opacity: "0.5", filter: "brightness(3)" },
          "100%": { transform: "scale(0)", opacity: "0", filter: "brightness(0)" },
        },
        "hyphae-grow": {
          "0%": { strokeDashoffset: "1000", opacity: "0" },
          "100%": { strokeDashoffset: "0", opacity: "1" },
        },
      },
      backgroundImage: {
        "grid-mycelium": `linear-gradient(rgba(91, 189, 214, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(91, 189, 214, 0.03) 1px, transparent 1px)`,
      },
      backgroundSize: {
        "grid-mycelium": "24px 24px",
      },
    },
  },
  plugins: [],
};

export default config;
