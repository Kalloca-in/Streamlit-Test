"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Award,
  CheckCircle2,
  Eye,
  Repeat,
  Sparkles,
  Trash2
} from "lucide-react";

import { api, DebriefBundle } from "@/lib/api";
import { cn, formatTime } from "@/lib/utils";

const STATUS_COPY: Record<string, { tone: string; label: string }> = {
  captured: { tone: "text-rust", label: "El atacante consiguió lo que buscaba" },
  victory: { tone: "text-moss", label: "Cortaste al atacante a tiempo" },
  left_dignified: { tone: "text-slate", label: "Saliste cuando lo necesitaste" },
  timed_out: { tone: "text-amber", label: "El tiempo cerró la sesión" },
  demo: { tone: "text-ink/60", label: "Demostración finalizada" }
};

export default function DebriefPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [bundle, setBundle] = useState<DebriefBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [wiped, setWiped] = useState<string[] | null>(null);

  useEffect(() => {
    api
      .debrief(id)
      .then(setBundle)
      .catch((e) => setError(e.message));
  }, [id]);

  async function wipe() {
    const r = await api.wipe(id);
    setWiped(r.removed_keys);
  }

  function close() {
    router.push("/");
  }

  if (error)
    return (
      <main className="mx-auto max-w-2xl px-6 py-16 text-center">
        <p className="text-rust">{error}</p>
        <Link href="/" className="btn mt-6">
          Volver al inicio
        </Link>
      </main>
    );

  if (!bundle)
    return (
      <main className="mx-auto max-w-2xl px-6 py-16 text-center text-ink/60">
        Preparando tu debrief…
      </main>
    );

  const status = STATUS_COPY[bundle.summary.status] || STATUS_COPY.left_dignified;

  return (
    <main className="mx-auto max-w-3xl px-6 py-12 space-y-12">
      {/* PART 1 — summary */}
      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card">
        <p className={cn("text-xs uppercase tracking-wide", status.tone)}>{status.label}</p>
        <h1 className="font-serif text-3xl mt-2">{bundle.summary.headline}</h1>
        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-sm text-ink/70">
          <span>Turnos: <span className="font-mono text-ink">{bundle.summary.turns}</span></span>
          <span>Duración: <span className="font-mono text-ink">{formatTime(bundle.summary.duration_seconds)}</span></span>
        </div>
      </motion.section>

      {/* PART 2 — confession */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.15, duration: 0.6 }}
        className="card border-ink/30 bg-bone/40"
      >
        <p className="text-xs uppercase tracking-wide text-ink/50 flex items-center gap-1.5">
          <Sparkles size={12} /> Confesión del atacante
        </p>
        <article className="mt-4 font-serif text-[17px] leading-relaxed text-ink whitespace-pre-line">
          {bundle.confession}
        </article>
      </motion.section>

      {/* PART 3 — annotated replay */}
      <section className="card">
        <p className="text-xs uppercase tracking-wide text-ink/50 flex items-center gap-1.5">
          <Eye size={12} /> Replay anotado
        </p>
        <ul className="mt-4 space-y-3">
          {bundle.annotations.length === 0 && (
            <li className="text-sm text-ink/50 italic">Sin anotaciones específicas para esta sesión.</li>
          )}
          {bundle.annotations.map((a, i) => (
            <li key={i} className="border-l-2 border-ink/30 pl-4 py-1">
              <p className="text-xs uppercase tracking-wide text-ink/50">
                Turno {a.turn_index} · {a.label}
              </p>
              <p className="text-sm text-ink/85 mt-1">{a.note}</p>
            </li>
          ))}
        </ul>
      </section>

      {/* PART 4 — replay */}
      {bundle.can_replay && (
        <section className="card border-amber/40 bg-amber/10">
          <p className="text-xs uppercase tracking-wide text-amber flex items-center gap-1.5">
            <Repeat size={12} /> Réplica del fracaso
          </p>
          <p className="mt-2 text-sm text-ink/85">
            Puedes volver a entrar a esta misma conversación, ahora con todo lo que acabas de leer en la cabeza.
            Es práctica deliberada inmediata: el aprendizaje más valioso suele estar a un intento de distancia.
          </p>
          <Link href="/configurar" className="btn-primary mt-4 inline-flex">
            Volver a intentarlo
          </Link>
        </section>
      )}

      {/* PART 5 — mirror */}
      {bundle.mirror_prompt && (
        <section className="text-center py-6">
          <p className="font-serif italic text-ink/75 text-lg max-w-2xl mx-auto leading-relaxed">
            {bundle.mirror_prompt}
          </p>
        </section>
      )}

      {/* PART 6 — verify deletion */}
      <section className="card border-ink/20">
        <p className="text-xs uppercase tracking-wide text-ink/50 flex items-center gap-1.5">
          <Trash2 size={12} /> Verificar borrado
        </p>
        <p className="mt-2 text-sm text-ink/75">
          Estos son los artefactos que se eliminarán al cerrar la sesión:
        </p>
        <ul className="mt-3 space-y-1 text-xs font-mono text-ink/80">
          {bundle.deletion_manifest.map((d, i) => (
            <li key={i} className="border-l-2 border-ink/20 pl-3">{d}</li>
          ))}
        </ul>
        {wiped ? (
          <div className="mt-5 flex items-center gap-2 text-moss text-sm">
            <CheckCircle2 size={16} /> Eliminados {wiped.length} artefactos. Puedes cerrar tranquilo.
          </div>
        ) : (
          <div className="mt-5 flex gap-3">
            <button onClick={wipe} className="btn-primary">
              Borrar y verificar
            </button>
          </div>
        )}
        {wiped && (
          <button onClick={close} className="btn mt-3">
            Cerrar sesión
          </button>
        )}
      </section>

      <footer className="text-center text-xs text-ink/40 py-4">
        <Award className="inline-block mr-1" size={11} />
        CiberSpar · sesión efímera · n cero compartido fuera de aquí
      </footer>
    </main>
  );
}
