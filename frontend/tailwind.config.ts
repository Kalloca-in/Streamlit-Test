import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Paleta sobria + acentos por rol (Bloque visual del briefing).
        background: "#0e0c0a",
        ink: "#f5efe6",
        paper: "#1a1714",
        muted: "#6b6259",
        // acentos por rol — consistentes en toda la app.
        ciudadano: "#d97757", // ladrillo cálido
        colaborador: "#5b9aa0", // teal apagado
        cliente: "#b48d4a", // ámbar metálico
        accent: "#e3b15c",
        danger: "#cc3d3d",
        ok: "#5fa86a",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["'Source Serif 4'", "Georgia", "serif"],
      },
      boxShadow: {
        bubble: "0 8px 28px rgba(0,0,0,.25)",
      },
    },
  },
  plugins: [],
};
export default config;
