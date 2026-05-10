"use client";
import { motion } from "framer-motion";
import type { Acto } from "@/lib/types";

export function MensajeSMS({ acto }: { acto: Acto }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="mx-auto max-w-md"
    >
      <div className="rounded-3xl bg-paper border border-white/5 shadow-bubble overflow-hidden">
        <div className="px-4 py-2 text-xs text-muted bg-black/30 flex justify-between">
          <span>SMS</span>
          <span>{acto.hora_dramatizada}</span>
        </div>
        <div className="px-5 py-4">
          <div className="text-xs text-muted mb-2">
            Remitente: <span className="text-ink">{acto.remitente_aparente}</span>
          </div>
          <div className="bg-blue-900/20 rounded-2xl px-4 py-3 text-sm leading-relaxed">
            {acto.cuerpo}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
