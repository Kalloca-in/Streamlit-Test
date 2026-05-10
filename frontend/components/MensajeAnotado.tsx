"use client";
import { useMemo, useState } from "react";
import type { Acto, Indicador } from "@/lib/types";
import { tipoIndicadorLabel } from "@/lib/utils";

type Segmento = { texto: string; indicador?: Indicador };

function partir(texto: string, inds: Indicador[]): Segmento[] {
  if (!texto) return [{ texto }];
  // Encuentra todas las posiciones de los fragmentos.
  const matches: { start: number; end: number; ind: Indicador }[] = [];
  for (const ind of inds) {
    const f = ind.fragmento;
    if (!f) continue;
    let i = 0;
    while (true) {
      const idx = texto.toLowerCase().indexOf(f.toLowerCase(), i);
      if (idx === -1) break;
      matches.push({ start: idx, end: idx + f.length, ind });
      i = idx + f.length;
    }
  }
  matches.sort((a, b) => a.start - b.start);
  // Resolver superposiciones quedándonos con la primera.
  const resolved: typeof matches = [];
  for (const m of matches) {
    if (resolved.length === 0 || m.start >= resolved[resolved.length - 1].end) {
      resolved.push(m);
    }
  }

  const segs: Segmento[] = [];
  let cursor = 0;
  for (const m of resolved) {
    if (cursor < m.start) segs.push({ texto: texto.slice(cursor, m.start) });
    segs.push({ texto: texto.slice(m.start, m.end), indicador: m.ind });
    cursor = m.end;
  }
  if (cursor < texto.length) segs.push({ texto: texto.slice(cursor) });
  return segs;
}

export function MensajeAnotado({
  acto,
  detectados,
  onToggle,
}: {
  acto: Acto;
  detectados: Set<string>;
  onToggle?: (indicadorId: string) => void;
}) {
  const [hover, setHover] = useState<string | null>(null);

  const cuerpoSegs = useMemo(
    () => partir(acto.cuerpo, acto.indicadores),
    [acto.cuerpo, acto.indicadores]
  );
  const asuntoSegs = useMemo(
    () => (acto.asunto ? partir(acto.asunto, acto.indicadores) : []),
    [acto.asunto, acto.indicadores]
  );
  const remitenteSegs = useMemo(
    () => partir(acto.remitente_aparente, acto.indicadores),
    [acto.remitente_aparente, acto.indicadores]
  );

  function pintar(segs: Segmento[]) {
    return segs.map((s, i) => {
      if (!s.indicador) return <span key={i}>{s.texto}</span>;
      const id = s.indicador.id;
      const isOn = detectados.has(id) || hover === id;
      return (
        <button
          key={i}
          type="button"
          onMouseEnter={() => setHover(id)}
          onMouseLeave={() => setHover(null)}
          onClick={() => onToggle?.(id)}
          className={`mx-0.5 px-1.5 py-0.5 rounded transition-colors text-left ${
            detectados.has(id)
              ? "bg-ok/25 border border-ok/40 text-ok"
              : isOn
              ? "bg-accent/25 border border-accent/40 text-accent"
              : "bg-accent/10 border border-accent/30 text-accent/90 hover:bg-accent/20"
          }`}
          title={s.indicador.explicacion}
        >
          {s.texto}
        </button>
      );
    });
  }

  return (
    <div className="card">
      <div className="text-xs text-muted">De: <span className="text-ink">{pintar(remitenteSegs)}</span></div>
      {acto.asunto && (
        <div className="text-xs text-muted mt-1">Asunto: <span className="text-ink">{pintar(asuntoSegs)}</span></div>
      )}
      <div className="mt-4 text-sm leading-relaxed">{pintar(cuerpoSegs)}</div>

      {hover && (
        <div className="mt-5 p-3 rounded-lg bg-black/30 border border-white/10 text-xs">
          <div className="text-accent font-medium mb-1">
            {tipoIndicadorLabel[acto.indicadores.find((i) => i.id === hover)?.tipo ?? ""]}
          </div>
          <div className="text-ink/85">
            {acto.indicadores.find((i) => i.id === hover)?.explicacion}
          </div>
        </div>
      )}
    </div>
  );
}
