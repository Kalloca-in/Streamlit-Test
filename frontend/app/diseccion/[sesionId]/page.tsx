"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { MensajeAnotado } from "@/components/MensajeAnotado";
import { RolPill } from "@/components/RolPill";
import { ganchoLabel, horaPorRol, tipoIndicadorLabel } from "@/lib/utils";
import type { DiaTriple, Indicador, Personaje, Rol, Sesion, TipoIndicador } from "@/lib/types";

export default function DiseccionPage() {
  const { sesionId } = useParams<{ sesionId: string }>();
  const router = useRouter();
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [dt, setDt] = useState<DiaTriple | null>(null);
  const [personaje, setPersonaje] = useState<Personaje | null>(null);
  const [detectados, setDetectados] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!sesionId) return;
    (async () => {
      const s = await api.obtenerSesion(sesionId);
      setSesion(s);
      const [d, p] = await Promise.all([
        api.obtenerDiaTriple(s.dia_triple_id),
        api.obtenerPersonaje(s.personaje_id),
      ]);
      setDt(d);
      setPersonaje(p);
    })();
  }, [sesionId]);

  function toggle(id: string) {
    setDetectados((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const tiposPorActo = useMemo(() => {
    if (!dt) return {};
    const map: Record<string, TipoIndicador[]> = {};
    for (const a of dt.actos) {
      map[a.id] = Array.from(new Set(a.indicadores.map((i) => i.tipo))) as TipoIndicador[];
    }
    return map;
  }, [dt]);

  if (!dt || !personaje) return <div className="max-w-3xl mx-auto px-6 py-16 text-muted">Cargando…</div>;

  // Tipos comunes a los tres actos
  const interseccion = (() => {
    if (!dt.actos.length) return [] as TipoIndicador[];
    const sets = dt.actos.map((a) => new Set(tiposPorActo[a.id] ?? []));
    const base = sets[0];
    return Array.from(base).filter((t) => sets.every((s) => s.has(t))) as TipoIndicador[];
  })();

  return (
    <div className="max-w-6xl mx-auto px-6 pt-10 pb-24">
      <header className="mb-6">
        <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">Sala de Disección</p>
        <h1 className="serif text-3xl md:text-4xl">
          Tres mensajes. Un solo gancho:{" "}
          <span className="text-accent">{ganchoLabel[dt.gancho_psicologico_raiz]}</span>.
        </h1>
        <p className="text-sm text-muted mt-2 max-w-3xl">
          Pasa el cursor sobre los textos resaltados para ver la explicación. Toca cualquiera para
          marcarlo como detectado. Lo común a los tres actos vive abajo.
        </p>
      </header>

      <div className="grid lg:grid-cols-3 gap-6">
        {dt.actos.map((a) => (
          <div key={a.id} className="space-y-3">
            <div className="flex items-center gap-3">
              <RolPill rol={a.rol as Rol} />
              <span className="text-xs text-muted">{horaPorRol[a.rol]}</span>
            </div>
            <MensajeAnotado acto={a} detectados={detectados} onToggle={toggle} />
            <div className="text-xs text-muted">
              Indicadores en este acto:{" "}
              {(tiposPorActo[a.id] ?? []).map((t) => (
                <span key={t} className="inline-block mr-1 mb-1 px-2 py-0.5 rounded border border-white/10">
                  {tipoIndicadorLabel[t]}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <section className="mt-10 card">
        <h2 className="serif text-xl mb-2">Lo que se repitió en los tres</h2>
        {interseccion.length === 0 ? (
          <p className="text-sm text-muted">No detectamos intersección directa de tipos. Mira las semejanzas en el patrón.</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {interseccion.map((t) => (
              <li key={t} className="px-3 py-1 rounded-full bg-accent/15 border border-accent/30 text-accent text-xs">
                {tipoIndicadorLabel[t]}
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="mt-10 flex justify-end">
        <button onClick={() => router.push(`/reflejo/${sesionId}`)} className="btn-primary">
          Ir a Mi Reflejo
        </button>
      </div>
    </div>
  );
}
