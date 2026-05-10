"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { api, Catalogs, SessionConfigPayload } from "@/lib/api";
import { cn } from "@/lib/utils";
import Link from "next/link";

const LEVEL_DESCRIPTIONS: Record<number, string> = {
  1: "Atacante torpe. Errores obvios. Para calibrar.",
  2: "Atacante básico. Una técnica clara.",
  3: "Atacante competente. Cambia de táctica si rechazas.",
  4: "Atacante hábil. Combina dos ganchos.",
  5: "Atacante experimentado. Lee tu estilo y adapta.",
  6: "Atacante profesional. Aprende rápido de tu defensa.",
  7: "Atacante estratega. Construye narrativa multi-turno.",
  8: "Atacante especialista. Personalizado al rol del personaje.",
  9: "Atacante de élite. Combina múltiples vectores psicológicos.",
  10: "Atacante de nivel APT. Indistinguible de un humano experto.",
  11: "Modo Demostración (no jugable) — observas, no juegas.",
  12: "Modo Caja Negra Estructural — el foco es invocar controles, no resistir solo."
};

export default function ConfigurarPage() {
  const router = useRouter();
  const [catalogs, setCatalogs] = useState<Catalogs | null>(null);
  const [level, setLevel] = useState<number>(3);
  const [archetype, setArchetype] = useState<string | null>(null);
  const [characterCode, setCharacterCode] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.catalogs().then(setCatalogs).catch((e) => setError(e.message));
  }, []);

  const requiresCharacter = useMemo(() => [6, 7, 8, 9, 10, 12].includes(level), [level]);
  const archetypeIsRandom = useMemo(() => [1, 2, 3, 4, 5].includes(level), [level]);

  async function start() {
    setError(null);
    setSubmitting(true);
    try {
      if (level === 11) {
        router.push("/demo");
        return;
      }
      const payload: SessionConfigPayload = {
        level,
        defender_kind: requiresCharacter ? "universal_character" : "self",
        ...(requiresCharacter && { universal_character_code: characterCode || undefined }),
        ...(requiresCharacter && archetype ? { archetype } : {})
      };
      const created = await api.createSession(payload);
      const target = level === 12 ? `/sparring/${created.session_id}?mode=caja-negra` : `/sparring/${created.session_id}`;
      router.push(target);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  const canStart = useMemo(() => {
    if (level === 11) return true;
    if (requiresCharacter) return !!archetype && !!characterCode;
    return true;
  }, [level, requiresCharacter, archetype, characterCode]);

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="flex items-center justify-between">
        <Link href="/" className="text-sm text-ink/60 hover:underline">← volver</Link>
        <h1 className="font-serif text-2xl">Configurar tu sparring</h1>
        <span />
      </header>

      {error && (
        <div className="mt-6 card border-rust/40 bg-rust/10 text-rust">
          <p className="text-sm">{error}</p>
        </div>
      )}

      <section className="mt-10 grid gap-8">
        <div className="card">
          <h2 className="font-serif text-lg">Bloque A — Nivel de intensidad</h2>
          <p className="text-sm text-ink/60 mt-1">
            Una vez iniciada la sesión, el nivel no se cambia. La integridad pedagógica depende de eso.
          </p>
          <div className="mt-5 grid grid-cols-6 sm:grid-cols-12 gap-2">
            {Array.from({ length: 12 }, (_, i) => i + 1).map((n) => (
              <button
                key={n}
                onClick={() => {
                  setLevel(n);
                  if ([1, 2, 3, 4, 5].includes(n)) {
                    setArchetype(null);
                    setCharacterCode(null);
                  }
                }}
                className={cn(
                  "h-12 rounded-md border text-sm font-mono transition-all",
                  level === n
                    ? "bg-ink text-paper border-ink"
                    : "bg-paper text-ink border-ink/20 hover:border-ink"
                )}
              >
                {n}
              </button>
            ))}
          </div>
          <motion.p
            key={level}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 text-sm text-ink/80 italic"
          >
            {LEVEL_DESCRIPTIONS[level]}
          </motion.p>
        </div>

        <div className="card">
          <h2 className="font-serif text-lg">Bloque B — Arquetipo del atacante</h2>
          {archetypeIsRandom ? (
            <p className="mt-3 text-sm text-ink/70">
              En este nivel, el arquetipo se asigna al azar. No sabrás quién enfrentaste hasta el debrief —
              parte del aprendizaje es notar quién es sin que te lo digan.
            </p>
          ) : (
            <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-3">
              {catalogs?.archetypes.map((a) => (
                <button
                  key={a.code}
                  onClick={() => setArchetype(a.code)}
                  className={cn(
                    "text-left p-4 rounded-md border transition-all",
                    archetype === a.code
                      ? "border-ink bg-ink/5"
                      : "border-ink/15 hover:border-ink/40"
                  )}
                  style={archetype === a.code ? { boxShadow: `inset 4px 0 0 0 ${a.accent_color}` } : {}}
                >
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ background: a.accent_color }} />
                    <span className="font-medium">{a.display_name}</span>
                  </div>
                  <p className="mt-2 text-xs text-ink/70">{a.short_description}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="font-serif text-lg">Bloque C — Identidad del defensor</h2>
          {!requiresCharacter && level !== 11 && (
            <p className="mt-3 text-sm text-ink/70">
              En este nivel juegas como tú mismo. No necesitas configurar nada más.
            </p>
          )}
          {level === 11 && (
            <p className="mt-3 text-sm text-ink/70">
              El nivel 11 es una demostración. Verás a un personaje ficticio enfrentando a un atacante de
              élite. No juegas; observas y aprendes el patrón.
            </p>
          )}
          {requiresCharacter && (
            <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-3">
              {catalogs?.universal_characters.map((c) => (
                <button
                  key={c.code}
                  onClick={() => setCharacterCode(c.code)}
                  className={cn(
                    "text-left p-4 rounded-md border transition-all",
                    characterCode === c.code
                      ? "border-ink bg-ink/5"
                      : "border-ink/15 hover:border-ink/40"
                  )}
                >
                  <p className="font-medium">{c.display_name}</p>
                  <p className="text-xs text-ink/60 mt-0.5">{c.role_title}</p>
                  <p className="text-xs text-ink/55 mt-2">{c.exposure_profile}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      </section>

      <div className="mt-10 flex items-center justify-end">
        <button
          onClick={start}
          disabled={!canStart || submitting}
          className={cn("btn-primary", (!canStart || submitting) && "opacity-40 pointer-events-none")}
        >
          {submitting ? "Iniciando…" : level === 11 ? "Ver demostración" : "Empezar sparring"}
        </button>
      </div>
    </main>
  );
}
