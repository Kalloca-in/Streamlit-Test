"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import { Dramatizacion } from "@/components/Dramatizacion";
import { DecisionPanel } from "@/components/DecisionPanel";
import { RolPill } from "@/components/RolPill";
import { Timeline } from "@/components/Timeline";
import { ganchoLabel, horaPorRol, rolLabel } from "@/lib/utils";
import type { Acto, DiaTriple, OpcionDecision, Personaje, Sesion } from "@/lib/types";

export default function DiaTriplePage() {
  const { sesionId } = useParams<{ sesionId: string }>();
  const router = useRouter();
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [dt, setDt] = useState<DiaTriple | null>(null);
  const [personaje, setPersonaje] = useState<Personaje | null>(null);
  const [paso, setPaso] = useState(1); // 1..3 = actos; 4 = revelación
  const [enviando, setEnviando] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!sesionId) return;
    (async () => {
      try {
        const s = await api.obtenerSesion(sesionId);
        setSesion(s);
        const [d, p] = await Promise.all([
          api.obtenerDiaTriple(s.dia_triple_id),
          api.obtenerPersonaje(s.personaje_id),
        ]);
        setDt(d);
        setPersonaje(p);
      } catch (e: any) {
        setErr(String(e));
      }
    })();
  }, [sesionId]);

  const actoActual = useMemo<Acto | null>(() => {
    if (!dt) return null;
    if (paso > 3) return null;
    return dt.actos.find((a) => a.orden === paso) ?? null;
  }, [dt, paso]);

  async function elegir(op: OpcionDecision) {
    if (!sesion || !actoActual) return;
    setEnviando(true);
    try {
      await api.registrarDecision(sesion.id, {
        acto_id: actoActual.id,
        rol: actoActual.rol,
        opcion_elegida: op.id,
        indicadores_detectados: [],
      });
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setEnviando(false);
    }
  }

  function avanzar() {
    setPaso((p) => Math.min(p + 1, 4));
  }

  if (err) return <div className="max-w-3xl mx-auto px-6 py-16 text-danger">{err}</div>;
  if (!dt || !personaje) return <div className="max-w-3xl mx-auto px-6 py-16 text-muted">Cargando…</div>;

  return (
    <div className="max-w-4xl mx-auto px-6 pt-10 pb-24">
      <header className="mb-6">
        <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">
          El Día Triple de {personaje.nombre}
        </p>
        <h1 className="serif text-3xl md:text-4xl">{dt.titulo}</h1>
        <p className="text-sm text-muted mt-1">
          Gancho raíz: <span className="text-accent">{ganchoLabel[dt.gancho_psicologico_raiz]}</span>
          {" · "}Nivel {dt.nivel_dificultad}/3
        </p>
      </header>

      <Timeline actos={dt.actos} actoActivo={paso} />

      <AnimatePresence mode="wait">
        {paso <= 3 && actoActual && (
          <motion.section
            key={`acto-${paso}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.4 }}
            className="mt-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <RolPill rol={actoActual.rol} />
              <span className="text-xs text-muted">{horaPorRol[actoActual.rol]}</span>
            </div>

            <Dramatizacion acto={actoActual} />

            <DecisionPanel
              pregunta={`¿Qué harías tú si fueras ${personaje.nombre.split(" ")[0]}?`}
              opciones={actoActual.opciones_decision}
              onElegir={elegir}
              disabled={enviando}
            />

            <div className="mt-8 flex justify-end">
              <button onClick={avanzar} className="btn-primary">
                {paso < 3 ? `Continuar al Acto ${paso + 1}` : "Ver la revelación"}
              </button>
            </div>
          </motion.section>
        )}

        {paso === 4 && (
          <motion.section
            key="revelacion"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-10"
          >
            <div className="rounded-2xl bg-gradient-to-br from-accent/15 via-paper to-paper border border-accent/30 p-8">
              <p className="text-xs uppercase tracking-[0.3em] text-accent">Revelación</p>
              <h2 className="serif text-3xl mt-3 mb-5">
                Cambió el disfraz. No cambió la trampa.
              </h2>
              <p className="text-ink/85 leading-relaxed whitespace-pre-line">
                {dt.nota_revelacion}
              </p>
            </div>

            <div className="mt-8 flex flex-wrap gap-3 justify-end">
              <button
                className="btn-ghost"
                onClick={() => router.push(`/diseccion/${sesionId}`)}
              >
                Entrar a la Sala de Disección
              </button>
              <button
                className="btn-primary"
                onClick={() => router.push(`/reflejo/${sesionId}`)}
              >
                Mi Reflejo
              </button>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      <p className="mt-12 text-xs text-muted text-center">
        Toda la dramatización es ficticia. Personaje, marca, banco y empresa: inventados.
      </p>
    </div>
  );
}
