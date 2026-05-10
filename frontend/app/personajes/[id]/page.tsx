"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { arquetipoLabel } from "@/lib/utils";
import { Avatar } from "@/components/Avatar";
import { sesionLocal } from "@/lib/sesion-local";
import type { DiaTriple, Personaje } from "@/lib/types";

export default function PersonajeDetalle() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [p, setP] = useState<Personaje | null>(null);
  const [dt, setDt] = useState<DiaTriple | null>(null);
  const [iniciando, setIniciando] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.obtenerPersonaje(id),
      api.listarDiasTriplesPorPersonaje(id),
    ])
      .then(([per, dts]) => {
        setP(per);
        setDt(dts[0] ?? null);
      })
      .catch((e) => setErr(String(e)));
  }, [id]);

  async function vivirElDia() {
    if (!p || !dt) return;
    setIniciando(true);
    try {
      // Crea organización demo + usuario anónimo si no existen.
      let orgId = sesionLocal.getOrganizacionId();
      let userId = sesionLocal.getUsuarioId();
      if (!orgId) {
        const org = await api.crearOrganizacion({
          nombre: "Org Demo Pública",
          slug: `org-demo-${Date.now().toString(36)}`,
          sector: "demo",
        });
        orgId = org.id;
        sesionLocal.setOrganizacionId(orgId);
      }
      if (!userId) {
        const u = await api.crearUsuarioAnonimo(orgId, `anon-${crypto.randomUUID()}`);
        userId = u.id;
        sesionLocal.setUsuarioId(userId);
      }
      const s = await api.crearSesion({
        usuario_id: userId,
        personaje_id: p.id,
        dia_triple_id: dt.id,
      });
      sesionLocal.setSesionActual(s.id);
      router.push(`/dia-triple/${s.id}`);
    } catch (e: any) {
      setErr(String(e));
      setIniciando(false);
    }
  }

  if (err) return <div className="max-w-3xl mx-auto px-6 py-16 text-danger">{err}</div>;
  if (!p) return <div className="max-w-3xl mx-auto px-6 py-16 text-muted">Cargando…</div>;

  return (
    <div className="max-w-3xl mx-auto px-6 pt-10 pb-24">
      <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">Onboarding · 2 de 4</p>
      <div className="flex items-center gap-5 mb-6">
        <Avatar name={p.nombre} size={88} />
        <div>
          <h1 className="serif text-4xl">{p.nombre}</h1>
          <p className="text-ink/70">
            {p.edad} años · {p.cargo_ficticio} en {p.empresa_ficticia}
          </p>
          <p className="text-accent text-sm mt-1">{arquetipoLabel[p.arquetipo]}</p>
        </div>
      </div>

      <div className="card mb-4">
        <h2 className="serif text-xl mb-2">Su contexto</h2>
        <p className="text-sm text-ink/85">{p.contexto_familiar}</p>
        <p className="text-sm text-ink/85 mt-3">{p.habitos_consumo}</p>
      </div>

      <div className="card mb-4">
        <h2 className="serif text-xl mb-3">Vector de exposición</h2>
        <Listado titulo="Redes" items={p.vector_exposicion.redes} />
        <Listado titulo="Rutinas" items={p.vector_exposicion.rutinas} />
        <Listado titulo="Consumos" items={p.vector_exposicion.consumos} />
      </div>

      {dt ? (
        <div className="card mb-6">
          <h2 className="serif text-xl mb-2">{dt.titulo}</h2>
          <p className="text-sm text-muted">
            Gancho psicológico raíz: <span className="text-accent">{dt.gancho_psicologico_raiz}</span>
          </p>
          <p className="text-sm text-muted">Nivel: {dt.nivel_dificultad}/3</p>
        </div>
      ) : (
        <p className="text-muted text-sm">Este personaje aún no tiene un Día Triple cargado.</p>
      )}

      <div className="flex gap-3 mt-8">
        <button onClick={vivirElDia} disabled={!dt || iniciando} className="btn-primary disabled:opacity-50">
          {iniciando ? "Iniciando…" : "Vivir su día"}
        </button>
      </div>

      <p className="text-xs text-muted mt-6">
        Personaje ficticio. Cualquier parecido con personas reales es coincidencia.
      </p>
    </div>
  );
}

function Listado({ titulo, items }: { titulo: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div className="mb-3">
      <div className="text-xs uppercase tracking-wider text-muted mb-1">{titulo}</div>
      <ul className="text-sm text-ink/85 list-disc list-inside space-y-1">
        {items.map((i) => (
          <li key={i}>{i}</li>
        ))}
      </ul>
    </div>
  );
}
