"use client";
import { motion } from "framer-motion";
import type { Acto, Rol } from "@/lib/types";
import { rolLabel, horaPorRol } from "@/lib/utils";

export function Timeline({ actos, actoActivo }: { actos: Acto[]; actoActivo: number }) {
  return (
    <div className="flex items-center justify-between gap-2 max-w-3xl mx-auto py-6 px-4">
      {actos.map((a, idx) => {
        const activo = idx + 1 === actoActivo;
        const cumplido = idx + 1 < actoActivo;
        const colorVar = `--tw-color-${a.rol}`;
        const colorClass =
          a.rol === "ciudadano"
            ? "border-ciudadano text-ciudadano"
            : a.rol === "colaborador"
            ? "border-colaborador text-colaborador"
            : "border-cliente text-cliente";
        return (
          <div key={a.id} className="flex-1 flex flex-col items-center gap-1">
            <motion.div
              initial={{ scale: 0.85, opacity: 0.5 }}
              animate={{ scale: activo ? 1.1 : 1, opacity: activo || cumplido ? 1 : 0.5 }}
              className={`w-10 h-10 rounded-full grid place-items-center border ${colorClass} ${
                activo ? "bg-white/5" : ""
              }`}
            >
              {idx + 1}
            </motion.div>
            <div className="text-[11px] uppercase tracking-wider text-muted">
              {rolLabel[a.rol as Rol]}
            </div>
            <div className="text-[11px] text-muted">{horaPorRol[a.rol as Rol]?.split(" — ")[0]}</div>
            {idx < actos.length - 1 && (
              <div className="hidden md:block w-full h-px bg-white/10 absolute" />
            )}
          </div>
        );
      })}
    </div>
  );
}
