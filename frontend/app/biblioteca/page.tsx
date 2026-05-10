"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Avatar } from "@/components/Avatar";
import { ganchoLabel, arquetipoLabel } from "@/lib/utils";
import type { DiaTriple, GanchoPsicologico, Personaje } from "@/lib/types";

interface CasoBiblioteca {
  personaje: Personaje;
  dia_triple: DiaTriple;
}

export default function BibliotecaPage() {
  const [casos, setCasos] = useState<CasoBiblioteca[]>([]);
  const [filtroGancho, setFiltroGancho] = useState<GanchoPsicologico | "todos">("todos");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const personajes = await api.listarPersonajes({ soloSemilla: true });
        const out: CasoBiblioteca[] = [];
        for (const p of personajes) {
          const dts = await api.listarDiasTriplesPorPersonaje(p.id);
          if (dts[0]) out.push({ personaje: p, dia_triple: dts[0] });
        }
        setCasos(out);
      } catch (e: any) {
        setErr(String(e));
      }
    })();
  }, []);

  const ganchos = useMemo(
    () =>
      Array.from(
        new Set(casos.map((c) => c.dia_triple.gancho_psicologico_raiz))
      ) as GanchoPsicologico[],
    [casos]
  );

  const filtrados =
    filtroGancho === "todos"
      ? casos
      : casos.filter((c) => c.dia_triple.gancho_psicologico_raiz === filtroGancho);

  return (
    <div className="max-w-6xl mx-auto px-6 pt-12 pb-24">
      <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">Biblioteca de casos</p>
      <h1 className="serif text-3xl md:text-4xl">
        El mismo gancho, mil disfraces.
      </h1>
      <p className="text-ink/75 mt-2 max-w-2xl">
        Explora los Días Triples por gancho psicológico raíz. Verás cómo el mismo
        atajo mental se repite en escenarios y arquetipos distintos.
      </p>

      <div className="mt-6 mb-8 flex gap-2 flex-wrap">
        <button
          onClick={() => setFiltroGancho("todos")}
          className={`px-3 py-1 rounded-full border text-xs ${
            filtroGancho === "todos" ? "bg-accent text-background border-accent" : "border-white/10"
          }`}
        >
          Todos
        </button>
        {ganchos.map((g) => (
          <button
            key={g}
            onClick={() => setFiltroGancho(g)}
            className={`px-3 py-1 rounded-full border text-xs ${
              filtroGancho === g ? "bg-accent text-background border-accent" : "border-white/10"
            }`}
          >
            {ganchoLabel[g]}
          </button>
        ))}
      </div>

      {err && <p className="text-danger text-sm">{err}</p>}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtrados.map(({ personaje, dia_triple }) => (
          <div key={dia_triple.id} className="card flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <Avatar name={personaje.nombre} size={48} />
              <div>
                <div className="serif text-lg leading-tight">{personaje.nombre}</div>
                <div className="text-xs text-muted">{arquetipoLabel[personaje.arquetipo]}</div>
              </div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-accent">
                Gancho raíz: {ganchoLabel[dia_triple.gancho_psicologico_raiz]}
              </div>
              <div className="serif text-base mt-1">{dia_triple.titulo}</div>
            </div>
            <p className="text-xs text-muted line-clamp-3">{dia_triple.nota_revelacion}</p>
            <div className="mt-auto">
              <Link href={`/personajes/${personaje.id}`} className="btn-ghost text-sm">
                Vivir este caso
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
