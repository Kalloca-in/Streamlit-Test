"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Pause, Play, Rewind, ShieldCheck } from "lucide-react";

import { api, DemoBundle } from "@/lib/api";
import { Avatar } from "@/components/Avatar";
import { cn } from "@/lib/utils";

export default function DemoPage() {
  const [bundle, setBundle] = useState<DemoBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState<1 | 2 | 3>(1);
  const [showAnnotations, setShowAnnotations] = useState(true);

  useEffect(() => {
    api.demoLevel11().then(setBundle).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!bundle || !playing) return;
    if (step >= bundle.script.length) return;
    const t = setTimeout(() => setStep((s) => s + 1), 3500 / speed);
    return () => clearTimeout(t);
  }, [bundle, playing, step, speed]);

  if (error)
    return (
      <main className="mx-auto max-w-2xl px-6 py-16 text-center">
        <p className="text-rust">{error}</p>
        <Link href="/" className="btn mt-6">Volver</Link>
      </main>
    );

  if (!bundle)
    return <main className="mx-auto max-w-2xl px-6 py-16 text-center text-ink/60">Cargando demostración…</main>;

  const visible = bundle.script.slice(0, step);
  const finished = step >= bundle.script.length;

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <header className="flex items-center justify-between">
        <Link href="/" className="text-sm text-ink/60 hover:underline">← volver</Link>
        <h1 className="font-serif text-2xl">Demostración · Nivel 11</h1>
        <span />
      </header>

      <p className="mt-2 text-sm text-ink/70 text-center">{bundle.title}</p>
      <p className="mt-4 text-sm text-ink/70">{bundle.description}</p>

      <div className="mt-6 flex items-center gap-2 justify-end text-xs text-ink/60">
        <button onClick={() => setStep(0)} className="btn-ghost"><Rewind size={14} /> Reiniciar</button>
        <button onClick={() => setPlaying((p) => !p)} className="btn">
          {playing ? <><Pause size={14} /> Pausa</> : <><Play size={14} /> Play</>}
        </button>
        <select
          value={speed}
          onChange={(e) => setSpeed(parseInt(e.target.value) as 1 | 2 | 3)}
          className="border border-ink/20 bg-paper rounded-md px-2 py-1 text-xs"
        >
          <option value={1}>1x</option>
          <option value={2}>2x</option>
          <option value={3}>3x</option>
        </select>
        <button onClick={() => setShowAnnotations((s) => !s)} className="btn-ghost">
          {showAnnotations ? "Ocultar" : "Ver"} anotaciones
        </button>
      </div>

      <section className="mt-6 space-y-4">
        <AnimatePresence initial={false}>
          {visible.map((entry, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <div className={cn("flex w-full", entry.role === "defender" ? "justify-end" : "justify-start")}>
                {entry.role === "attacker" && <Avatar archetype={bundle.archetype} />}
                <div
                  className={cn(
                    "ml-3 mr-3",
                    entry.role === "attacker" ? "chat-bubble-attacker" : "chat-bubble-defender"
                  )}
                >
                  {entry.content}
                </div>
              </div>
              {showAnnotations && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="text-[12px] italic text-ink/60 mt-1 ml-14 mr-14 border-l-2 border-ink/20 pl-3"
                >
                  {entry.annotation}
                </motion.div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </section>

      {finished && (
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-12 card border-ink/30 bg-bone/30"
        >
          <p className="text-xs uppercase tracking-wide text-ink/50 flex items-center gap-1.5">
            <ShieldCheck size={12} /> Cierre
          </p>
          <h2 className="font-serif text-xl mt-2">{bundle.closing.headline}</h2>
          <ul className="mt-5 space-y-3">
            {bundle.closing.controls_that_would_have_stopped_it.map((c) => (
              <li key={c.code} className="border-l-2 border-ink/30 pl-4">
                <p className="font-medium">{c.display_name || c.code}</p>
                <p className="text-sm text-ink/75 mt-1">{c.lesson}</p>
              </li>
            ))}
          </ul>
          <Link href="/configurar" className="btn-primary mt-6 inline-flex">
            Ahora juega tú
          </Link>
        </motion.section>
      )}
    </main>
  );
}
