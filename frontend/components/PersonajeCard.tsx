"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { Avatar } from "./Avatar";
import type { Personaje } from "@/lib/types";
import { arquetipoLabel } from "@/lib/utils";

export function PersonajeCard({ p }: { p: Personaje }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="card flex flex-col gap-4 hover:border-white/20"
    >
      <div className="flex items-center gap-4">
        <Avatar name={p.nombre} size={64} />
        <div>
          <h3 className="serif text-xl">{p.nombre}</h3>
          <p className="text-sm text-muted">
            {p.edad} · {p.cargo_ficticio}
          </p>
          <p className="text-xs mt-1 text-accent">{arquetipoLabel[p.arquetipo]}</p>
        </div>
      </div>

      <p className="text-sm text-ink/80 line-clamp-3">{p.contexto_familiar}</p>

      <div className="flex flex-wrap gap-2">
        {p.marcas_asociadas.slice(0, 3).map((m) => (
          <span key={m} className="text-[10px] uppercase tracking-wide text-muted border border-white/10 rounded px-2 py-1">
            {m}
          </span>
        ))}
      </div>

      <div className="mt-auto flex items-center justify-between">
        <span className="text-xs text-muted">Nivel sugerido: {p.nivel_sugerido}/3</span>
        <Link href={{ pathname: "/personajes/" + p.id }} className="btn-primary text-sm">
          Conocer
        </Link>
      </div>
    </motion.div>
  );
}
