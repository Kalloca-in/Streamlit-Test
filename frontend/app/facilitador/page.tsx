"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { sesionLocal } from "@/lib/sesion-local";
import type { ReporteAgregado, Rol } from "@/lib/types";
import { rolLabel } from "@/lib/utils";

export default function FacilitadorPage() {
  const [orgId, setOrgId] = useState<string>("");
  const [rep, setRep] = useState<ReporteAgregado | null>(null);
  const [cargando, setCargando] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    setOrgId(sesionLocal.getOrganizacionId() ?? "");
  }, []);

  async function cargar() {
    if (!orgId) return;
    setCargando(true);
    setErr(null);
    try {
      const r = await api.reporteAgregado(orgId);
      setRep(r);
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setCargando(false);
    }
  }

  const insuficiente = rep && rep.minimo_requerido !== undefined;

  return (
    <div className="max-w-4xl mx-auto px-6 pt-12 pb-24">
      <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">Modo Facilitador</p>
      <h1 className="serif text-3xl md:text-4xl">Reportes agregados, nunca individuales.</h1>
      <p className="text-ink/75 mt-2 max-w-2xl">
        El facilitador del cliente ve únicamente métricas agregadas, con un mínimo de
        respuestas para preservar el anonimato. No hay forma de descender a una respuesta
        individual.
      </p>

      <div className="card mt-8">
        <label className="block text-sm mb-2">ID de organización</label>
        <div className="flex gap-2">
          <input
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            placeholder="UUID de la organización"
            className="flex-1 bg-paper border border-white/10 rounded-xl px-3 py-2 text-sm font-mono"
          />
          <button onClick={cargar} disabled={!orgId || cargando} className="btn-primary">
            {cargando ? "Cargando…" : "Ver reporte"}
          </button>
        </div>
      </div>

      {err && <p className="text-danger mt-4 text-sm">{err}</p>}

      {rep && insuficiente && (
        <div className="card mt-8 border-yellow-500/30 bg-yellow-500/5">
          <div className="text-yellow-300 text-sm font-medium">N insuficiente</div>
          <p className="text-sm text-ink/80 mt-2">
            {rep.mensaje} (actual: {rep.n_actual}, mínimo: {rep.minimo_requerido}).
          </p>
        </div>
      )}

      {rep && !insuficiente && (
        <>
          <div className="grid sm:grid-cols-3 gap-4 mt-8">
            <Stat label="Usuarios con sesión completada" value={rep.n_usuarios_con_sesion_completada ?? 0} />
            <Stat label="Sesiones completadas" value={rep.n_sesiones_completadas ?? 0} />
            <Stat
              label="Tasa global de decisiones seguras"
              value={`${Math.round((rep.tasa_decisiones_seguras_global ?? 0) * 100)}%`}
            />
          </div>

          <h2 className="serif text-2xl mt-10 mb-3">Tasa por rol</h2>
          <div className="grid sm:grid-cols-3 gap-4">
            {(["ciudadano", "colaborador", "cliente"] as Rol[]).map((r) => {
              const t = rep.tasa_decisiones_seguras_por_rol?.[r] ?? 0;
              return (
                <div key={r} className="card">
                  <div className={`role-pill role-pill--${r} mb-3`}>{rolLabel[r]}</div>
                  <div className="text-3xl serif">{Math.round(t * 100)}%</div>
                </div>
              );
            })}
          </div>

          <p className="text-xs text-muted mt-10">{rep.advertencia}</p>
        </>
      )}
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
