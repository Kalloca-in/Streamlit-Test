import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1B1A1F",
        paper: "#F4F1EA",
        bone: "#E5DFD3",
        amber: "#C9885A",
        rust: "#B85450",
        slate: "#3F5E7C",
        moss: "#7BA098",
        plum: "#6E5B8A",
        olive: "#8C7A52"
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
        serif: ["ui-serif", "Georgia", "Cambria", "Times New Roman", "Times", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"]
      },
      keyframes: {
        typing: {
          "0%, 60%, 100%": { transform: "translateY(0)" },
          "30%": { transform: "translateY(-3px)" }
        }
      },
      animation: {
        typing: "typing 1.2s ease-in-out infinite"
      }
    }
  },
  plugins: []
};

export default config;
