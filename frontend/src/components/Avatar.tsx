"use client";
import { motion } from "framer-motion";

const PALETTES: Record<string, string> = {
  amigo_servicial: "#7BA098",
  autoridad_apurada: "#B85450",
  complice: "#6E5B8A",
  experto_tecnico: "#3F5E7C",
  bondadoso: "#C9885A",
  insider: "#8C7A52",
  unknown: "#888888"
};

export function Avatar({ archetype, size = 44 }: { archetype?: string | null; size?: number }) {
  const color = PALETTES[archetype || "unknown"] || PALETTES.unknown;
  return (
    <motion.svg
      initial={{ scale: 0.85, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
      width={size}
      height={size}
      viewBox="0 0 64 64"
      aria-hidden="true"
      className="shrink-0"
    >
      <rect width="64" height="64" rx="14" fill={color} fillOpacity="0.15" />
      <circle cx="32" cy="26" r="10" fill={color} fillOpacity="0.55" />
      <path
        d="M14 54c0-9 8-16 18-16s18 7 18 16"
        fill={color}
        fillOpacity="0.4"
      />
      <text
        x="32"
        y="34"
        textAnchor="middle"
        fontFamily="ui-monospace, monospace"
        fontSize="10"
        fill="#fff"
        opacity="0.85"
      >
        ?
      </text>
    </motion.svg>
  );
}
