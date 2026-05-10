"use client";
import { motion } from "framer-motion";
import type { Acto } from "@/lib/types";

export function MensajeWhatsApp({ acto }: { acto: Acto }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="mx-auto max-w-md"
    >
      <div className="rounded-3xl bg-[#0d1417] border border-white/5 shadow-bubble overflow-hidden">
        <div className="px-4 py-3 text-xs bg-[#0d2d1f] flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-700/60" />
          <div>
            <div className="text-ink text-sm">{acto.remitente_aparente}</div>
            <div className="text-muted text-[10px]">en línea · {acto.hora_dramatizada}</div>
          </div>
        </div>
        <div className="px-4 py-6 space-y-2 min-h-[200px]">
          <div className="bg-[#1f2c33] rounded-2xl rounded-tl-md px-4 py-2 text-sm leading-relaxed max-w-[85%]">
            {acto.cuerpo}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
