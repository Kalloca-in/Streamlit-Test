"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { sesionLocal } from "@/lib/sesion-local";
import type { ProgresoUsuario, Rol } from "@/lib/types";
import { rolLabel } from "@/lib/utils";

export default function Dashboard() {
  const [p, setP] = useState<ProgresoUsuario | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [sinSesion, setSinSesion] = useState(false);

  useEffect(() => {
    const uid = sesionLocal.getUsuarioId();
    if (!uid) {
      setSinSesion(true);
      return;
    }
    api.progresoUsuario(uid).then(setP).catch((e) => setErr(String(e)));
  }, []);

  if (sinSesion) {
    return (
      <div className="max-w-2xl mx-auto px-6 pt-20 text-center">
        <p className="text-xs uppercase tracking-[0.3em] text-accent">Dashboard</p>
        <h1 className="serif text-3xl mt-3 mb-4">Aún no has vivido un día.</h1>
        <p className="text-ink/80">Empieza eligiendo un personaje.</p>
        <Link className="btn-primary inline-block mt-6" href="/personajes">Elegir personaje</Link>
      </div>
    );
  }
  if (err) return <p className="text-danger px-6 pt-12">{err}</p>;
  if (!p) return <p className="text-muted px-6 pt-12">Cargando…</p>;

  const tasa = p.decisiones_totales
    ? Math.round((p.decisiones_seguras / p.decisiones_totales) * 100)
    : 0;

  return (
    <div className="max-w-4xl mx-auto px-6 pt-12 pb-24">
      <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">Mi progreso</p>
      <h1 className="serif text-3xl md:text-4xl mb-2">Tu coach, no tu inspector.</h1>
      <p className="text-ink/75">Lo que viste, lo que detectaste, lo que sigue.</p>

      <div className="grid sm:grid-cols-3 gap-4 mt-8">
        <Stat label="Días vividos" value={p.sesiones_completadas} />
        <Stat label="Decisiones tomadas" value={p.decisiones_totales} />
        <Stat label="Tasa de decisiones seguras" value={`${tasa}%`} />
      </div>

      <h2 className="serif text-2xl mt-12 mb-3">Por rol</h2>
      <div className="grid sm:grid-cols-3 gap-4">
        {(["ciudadano", "colaborador", "cliente"] as Rol[]).map((r) => {
          const stats = p.por_rol?.[r] ?? { total: 0, seguras: 0 };
          const t = stats.total ? Math.round((stats.seguras / stats.total) * 100) : 0;
          return (
            <div key={r} className="card">
              <div className={`role-pill role-pill--${r} mb-3`}>{rolLabel[r]}</div>
              <div className="text-3xl serif">{t}%</div>
              <div className="text-xs text-muted mt-1">
                {stats.seguras} seguras de {stats.total} decisiones
              </div>
            </div>
          );
        })}
      </div>

      <div className="card mt-12">
        <h3 className="serif text-lg mb-1">Próximo paso recomendado</h3>
        <p className="text-sm text-ink/80">
          Elige un personaje con un gancho psicológico distinto al que ya viviste. La
          biblioteca te ayuda a ver patrones cruzados.
        </p>
        <div className="mt-4 flex gap-3">
          <Link href="/personajes" className="btn-primary">Otro personaje</Link>
          <Link href="/biblioteca" className="btn-ghost">Biblioteca</Link>
        </div>
      </div>

      <p className="text-xs text-muted mt-12">
        Tus reflexiones son privadas. Tu empleador solo recibe reportes agregados y
        anónimos cuando hay suficientes participantes.
      </p>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card">
      <div className="text-3xl serif">{value}</div>
      <div className="text-xs uppercase tracking-wider text-muted mt-1">{label}</div>
    </div>
  );
}
