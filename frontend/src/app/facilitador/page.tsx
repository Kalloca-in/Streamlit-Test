"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Eye, ShieldOff, Users } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

type CharacterRow = {
  code: string;
  display_name: string;
  role_title: string;
  fictional_context: string;
  hierarchy_level: string | null;
};

type CapturesRow = { archetype: string; total: number; captures: number; capture_rate: number };
type HookRow = { hook: string; accepted: number; rejected: number; n: number; acceptance_rate: number };

export default function FacilitadorPage() {
  const [token, setToken] = useState("");
  const [orgSlug, setOrgSlug] = useState("");
  const [characters, setCharacters] = useState<CharacterRow[]>([]);
  const [captures, setCaptures] = useState<CapturesRow[]>([]);
  const [hooks, setHooks] = useState<HookRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [authed, setAuthed] = useState(false);

  // Character creation form
  const [code, setCode] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [roleTitle, setRoleTitle] = useState("");
  const [fictionalContext, setFictionalContext] = useState("");

  async function call<T>(path: string, init?: RequestInit): Promise<T> {
    const r = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "X-Facilitator-Token": token,
        ...(init?.headers || {})
      }
    });
    if (!r.ok) throw new Error(`${r.status} ${(await r.text()) || r.statusText}`);
    return r.json();
  }

  async function loadAll() {
    setError(null);
    try {
      setCharacters(await call<CharacterRow[]>(`/facilitator/orgs/${orgSlug}/characters`));
      const cap = await call<{ buckets: CapturesRow[] }>(`/facilitator/orgs/${orgSlug}/metrics/captures`);
      setCaptures(cap.buckets);
      const hk = await call<{ buckets: HookRow[] }>(`/facilitator/orgs/${orgSlug}/metrics/hooks`);
      setHooks(hk.buckets);
      setAuthed(true);
    } catch (e: any) {
      setError(e.message);
    }
  }

  async function createCharacter() {
    setError(null);
    try {
      await call(`/facilitator/orgs/${orgSlug}/characters`, {
        method: "POST",
        body: JSON.stringify({
          code,
          display_name: displayName,
          role_title: roleTitle,
          fictional_context: fictionalContext
        })
      });
      setCode(""); setDisplayName(""); setRoleTitle(""); setFictionalContext("");
      await loadAll();
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="flex items-center justify-between">
        <Link href="/" className="text-sm text-ink/60 hover:underline">← volver</Link>
        <h1 className="font-serif text-2xl">Panel del facilitador</h1>
        <span />
      </header>

      <div className="mt-4 card border-amber/40 bg-amber/10 text-sm flex items-start gap-3">
        <ShieldOff size={16} className="mt-0.5" />
        <p>
          Aquí solo verás métricas agregadas con n ≥ 10. No es posible asociar una caída
          específica a un colaborador identificable, ni siquiera a través de filtros cruzados.
        </p>
      </div>

      {!authed ? (
        <section className="mt-8 card">
          <h2 className="font-serif text-lg">Acceso</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
            <input
              value={orgSlug}
              onChange={(e) => setOrgSlug(e.target.value)}
              placeholder="org slug (ej: acme)"
              className="border border-ink/20 rounded-md px-3 py-2 text-sm"
            />
            <input
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="X-Facilitator-Token (debe empezar con fac_)"
              className="border border-ink/20 rounded-md px-3 py-2 text-sm font-mono"
            />
          </div>
          <button onClick={loadAll} className="btn-primary mt-4">Cargar panel</button>
          {error && <p className="text-rust text-sm mt-3">{error}</p>}
        </section>
      ) : (
        <>
          <section className="mt-10 card">
            <h2 className="font-serif text-lg flex items-center gap-2">
              <Users size={16} /> Personajes corporativos
            </h2>
            <p className="text-xs text-ink/60 mt-1">
              Arquetipos sin OSINT real. Solo cargo + contexto ficticio + nivel jerárquico.
            </p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2">
              {characters.map((c) => (
                <div key={c.code} className="border border-ink/15 rounded p-3 text-sm">
                  <p className="font-medium">{c.display_name}</p>
                  <p className="text-xs text-ink/60">{c.role_title}</p>
                  <p className="text-xs text-ink/60 mt-2">{c.fictional_context}</p>
                </div>
              ))}
              {characters.length === 0 && <p className="text-xs text-ink/50 italic">Aún sin personajes.</p>}
            </div>

            <details className="mt-6 border-t border-ink/10 pt-4">
              <summary className="cursor-pointer text-sm">Crear nuevo personaje</summary>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-3">
                <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="code (snake_case)" className="border border-ink/20 rounded px-3 py-2 text-sm" />
                <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="nombre del personaje" className="border border-ink/20 rounded px-3 py-2 text-sm" />
                <input value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} placeholder="cargo ficticio" className="border border-ink/20 rounded px-3 py-2 text-sm md:col-span-2" />
                <textarea value={fictionalContext} onChange={(e) => setFictionalContext(e.target.value)} placeholder="contexto ficticio (sin OSINT real)" rows={3} className="border border-ink/20 rounded px-3 py-2 text-sm md:col-span-2" />
              </div>
              <button onClick={createCharacter} className="btn-primary mt-3">Crear</button>
            </details>
          </section>

          <section className="mt-8 card">
            <h2 className="font-serif text-lg flex items-center gap-2">
              <Building2 size={16} /> Tasa de captura por arquetipo
            </h2>
            <table className="mt-4 w-full text-sm">
              <thead className="text-xs uppercase tracking-wide text-ink/50">
                <tr><th className="text-left py-2">Arquetipo</th><th className="text-right">Total</th><th className="text-right">Capturas</th><th className="text-right">Tasa</th></tr>
              </thead>
              <tbody>
                {captures.map((b) => (
                  <tr key={b.archetype} className="border-t border-ink/10">
                    <td className="py-2">{b.archetype}</td>
                    <td className="text-right font-mono">{b.total}</td>
                    <td className="text-right font-mono">{b.captures}</td>
                    <td className="text-right font-mono">{(b.capture_rate * 100).toFixed(0)}%</td>
                  </tr>
                ))}
                {captures.length === 0 && (
                  <tr><td colSpan={4} className="py-3 text-xs italic text-ink/50">Aún no hay buckets con n ≥ 10. La supresión es por diseño.</td></tr>
                )}
              </tbody>
            </table>
          </section>

          <section className="mt-8 card">
            <h2 className="font-serif text-lg flex items-center gap-2">
              <Eye size={16} /> Ganchos psicológicos en tu población
            </h2>
            <table className="mt-4 w-full text-sm">
              <thead className="text-xs uppercase tracking-wide text-ink/50">
                <tr><th className="text-left py-2">Gancho</th><th className="text-right">n</th><th className="text-right">Aceptados</th><th className="text-right">Rechazados</th><th className="text-right">Tasa de aceptación</th></tr>
              </thead>
              <tbody>
                {hooks.map((h) => (
                  <tr key={h.hook} className="border-t border-ink/10">
                    <td className="py-2">{h.hook}</td>
                    <td className="text-right font-mono">{h.n}</td>
                    <td className="text-right font-mono">{h.accepted}</td>
                    <td className="text-right font-mono">{h.rejected}</td>
                    <td className="text-right font-mono">{(h.acceptance_rate * 100).toFixed(0)}%</td>
                  </tr>
                ))}
                {hooks.length === 0 && (
                  <tr><td colSpan={5} className="py-3 text-xs italic text-ink/50">Aún no hay buckets con n ≥ 10.</td></tr>
                )}
              </tbody>
            </table>
          </section>
        </>
      )}
    </main>
  );
}
