"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { arquetipoLabel } from "@/lib/utils";
import { PersonajeCard } from "@/components/PersonajeCard";
import type { Arquetipo, Personaje } from "@/lib/types";

const ARQUETIPOS: Arquetipo[] = [
  "guardian_financiero",
  "arquitecto_digital",
  "rostro_experiencias",
  "cuidador_familiar",
  "ejecutivo_transito",
  "operador_confianza",
];

export default function PersonajesPage() {
  const [personajes, setPersonajes] = useState<Personaje[]>([]);
  const [arquetipo, setArquetipo] = useState<Arquetipo | "todos">("todos");
  const [nivel, setNivel] = useState<number | "todos">("todos");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    api
      .listarPersonajes({
        arquetipo: arquetipo === "todos" ? undefined : arquetipo,
        nivel: nivel === "todos" ? undefined : Number(nivel),
        soloSemilla: true,
      })
      .then(setPersonajes)
      .catch((e) => setError(String(e)));
  }, [arquetipo, nivel]);

  return (
    <div className="max-w-6xl mx-auto px-6 pt-12 pb-24">
      <header className="mb-10">
        <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">
          Onboarding · 1 de 4
        </p>
        <h1 className="serif text-4xl md:text-5xl">Elige a quien acompañarás hoy.</h1>
        <p className="mt-3 text-ink/70 max-w-2xl">
          Los seis son personajes ficticios. Vas a ver su día atravesado por tres
          ataques. Su nombre, su empresa, su banco —todo— está inventado.
        </p>
      </header>

      <div className="flex flex-wrap gap-3 mb-8 items-center">
        <select
          className="bg-paper border border-white/10 rounded-xl px-3 py-2 text-sm"
          value={arquetipo}
          onChange={(e) => setArquetipo(e.target.value as any)}
        >
          <option value="todos">Todos los arquetipos</option>
          {ARQUETIPOS.map((a) => (
            <option key={a} value={a}>
              {arquetipoLabel[a]}
            </option>
          ))}
        </select>
        <select
          className="bg-paper border border-white/10 rounded-xl px-3 py-2 text-sm"
          value={nivel}
          onChange={(e) =>
            setNivel(e.target.value === "todos" ? "todos" : Number(e.target.value))
          }
        >
          <option value="todos">Todos los niveles</option>
          <option value={1}>Introductorio</option>
          <option value={2}>Intermedio</option>
          <option value={3}>Avanzado</option>
        </select>
      </div>

      {error && (
        <div className="text-danger text-sm mb-6">No se pudo cargar el catálogo: {error}</div>
      )}

      <motion.div
        layout
        className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {personajes.map((p) => (
          <PersonajeCard key={p.id} p={p} />
        ))}
      </motion.div>
    </div>
  );
}
