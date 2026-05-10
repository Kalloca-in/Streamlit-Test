"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { OpcionDecision } from "@/lib/types";

export function DecisionPanel({
  pregunta,
  opciones,
  onElegir,
  disabled = false,
}: {
  pregunta: string;
  opciones: OpcionDecision[];
  onElegir: (op: OpcionDecision) => void | Promise<void>;
  disabled?: boolean;
}) {
  const [elegida, setElegida] = useState<OpcionDecision | null>(null);

  async function manejar(op: OpcionDecision) {
    if (elegida || disabled) return;
    setElegida(op);
    await onElegir(op);
  }

  return (
    <div className="mt-8">
      <h3 className="serif text-lg mb-3">{pregunta}</h3>
      <div className="grid gap-2 md:grid-cols-1">
        {opciones.map((op) => {
          const isElegida = elegida?.id === op.id;
          const verdict = isElegida ? (op.es_segura ? "ok" : "danger") : null;
          return (
            <button
              key={op.id}
              disabled={!!elegida || disabled}
              onClick={() => manejar(op)}
              className={`text-left rounded-xl border px-4 py-3 transition-all
                ${verdict === "ok" ? "border-ok bg-ok/10" : ""}
                ${verdict === "danger" ? "border-danger bg-danger/10" : ""}
                ${!verdict ? "border-white/10 hover:border-white/30 hover:bg-white/5" : ""}
                ${elegida && !isElegida ? "opacity-40" : ""}
              `}
            >
              <div className="flex items-start gap-3">
                <span className="text-xs uppercase tracking-wider text-muted mt-1">{op.id}</span>
                <span className="text-sm">{op.texto}</span>
              </div>
            </button>
          );
        })}
      </div>

      <AnimatePresence>
        {elegida && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`mt-4 text-sm rounded-xl px-4 py-3 border
              ${elegida.es_segura ? "border-ok/40 bg-ok/5 text-ok" : "border-danger/40 bg-danger/5 text-danger"}`}
          >
            <div className="font-medium mb-1">
              {elegida.es_segura ? "Decisión segura" : "Esto habría salido mal"}
            </div>
            <div className="text-ink/90">{elegida.consecuencia}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
