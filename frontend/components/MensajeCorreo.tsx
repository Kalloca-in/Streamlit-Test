"use client";
import { motion } from "framer-motion";
import type { Acto } from "@/lib/types";

export function MensajeCorreo({ acto }: { acto: Acto }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="mx-auto max-w-2xl"
    >
      <div className="rounded-2xl bg-paper border border-white/5 shadow-bubble overflow-hidden">
        <div className="px-5 py-3 border-b border-white/5 text-xs text-muted">
          <div>De: <span className="text-ink">{acto.remitente_aparente}</span></div>
          {acto.asunto && (
            <div>Asunto: <span className="text-ink">{acto.asunto}</span></div>
          )}
          <div>Hora: {acto.hora_dramatizada}</div>
        </div>
        <div className="px-6 py-5 text-sm leading-relaxed whitespace-pre-line">
          {acto.cuerpo}
        </div>
      </div>
    </motion.div>
  );
}
