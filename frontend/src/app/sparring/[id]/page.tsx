"use client";

import { use, useEffect, useMemo, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { LogOut, Send, ShieldCheck } from "lucide-react";

import { api, WS_BASE } from "@/lib/api";
import { cn, formatTime } from "@/lib/utils";
import { EphemeralBadge } from "@/components/EphemeralBadge";
import { Avatar } from "@/components/Avatar";
import { TypingIndicator } from "@/components/TypingIndicator";

type Message = {
  id: string;
  role: "attacker" | "defender" | "system";
  content: string;
  intercepted?: boolean;
};

type ServerMsg =
  | { type: "attacker_message"; content: string; turn: number; intercepted: boolean }
  | { type: "system"; content: string }
  | { type: "session_end"; status: string }
  | { type: "tick"; remaining_seconds: number }
  | { type: "error"; content: string };

export default function SparringPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const isCajaNegra = searchParams.get("mode") === "caja-negra";

  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [remaining, setRemaining] = useState<number>(30 * 60);
  const [typing, setTyping] = useState(true);
  const [ended, setEnded] = useState<string | null>(null);
  const [session, setSession] = useState<any | null>(null);
  const [controls, setControls] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getSession(id).then(setSession).catch(() => {});
    if (isCajaNegra) {
      api.catalogs().then((c) => setControls(c.organizational_controls)).catch(() => {});
    }
  }, [id, isCajaNegra]);

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/ws/sessions/${id}`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      const m: ServerMsg = JSON.parse(ev.data);
      if (m.type === "attacker_message") {
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "attacker", content: m.content, intercepted: m.intercepted }
        ]);
        setTyping(false);
      } else if (m.type === "system") {
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "system", content: m.content }]);
      } else if (m.type === "tick") {
        setRemaining(m.remaining_seconds);
      } else if (m.type === "session_end") {
        setEnded(m.status);
        setTimeout(() => router.push(`/debrief/${id}`), 1200);
      } else if (m.type === "error") {
        setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "system", content: m.content }]);
      }
    };
    ws.onclose = () => {
      setTyping(false);
    };
    return () => {
      ws.close();
    };
  }, [id, router]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  function send() {
    const text = draft.trim();
    if (!text || ended) return;
    wsRef.current?.send(JSON.stringify({ type: "user_message", content: text }));
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "defender", content: text }]);
    setDraft("");
    setTyping(true);
  }

  function exitDignified() {
    if (ended) return;
    wsRef.current?.send(JSON.stringify({ type: "exit", reason: "dignified" }));
    setTyping(false);
  }

  function invokeControl(code: string) {
    wsRef.current?.send(JSON.stringify({ type: "invoke_control", control_code: code }));
  }

  const archetype = session?.attacker?.archetype;
  const character = session?.defender?.character;

  const timerColor = useMemo(() => {
    if (remaining > 10 * 60) return "text-ink/70";
    if (remaining > 3 * 60) return "text-amber";
    return "text-rust";
  }, [remaining]);

  return (
    <main className="min-h-screen grid grid-cols-1 md:grid-cols-[260px_1fr_280px] bg-paper">
      {/* LEFT — persistent info */}
      <aside className="border-r border-ink/10 p-5 flex flex-col gap-5">
        <EphemeralBadge remaining={remaining} />
        <div>
          <p className="text-xs uppercase tracking-wide text-ink/50">Tiempo restante</p>
          <p className={cn("font-mono text-3xl mt-1", timerColor)}>{formatTime(remaining)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-ink/50">Turno</p>
          <p className="font-mono text-lg mt-1">{messages.filter((m) => m.role !== "system").length}</p>
        </div>
        <button onClick={exitDignified} className="btn mt-auto" disabled={!!ended}>
          <LogOut size={14} /> Salir con dignidad
        </button>
        <p className="text-[11px] text-ink/50 leading-snug">
          Salir no es derrota. La salida también es entrenamiento. No queda registrado como abandono.
        </p>
      </aside>

      {/* CENTER — chat */}
      <section className="flex flex-col min-h-screen">
        <div className="border-b border-ink/10 px-5 py-3 flex items-center gap-3">
          <Avatar archetype={archetype} />
          <div>
            <p className="text-sm font-medium">Conversación en curso</p>
            <p className="text-xs text-ink/50">Mantén el chat. Responde como lo harías de verdad.</p>
          </div>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-6 space-y-3 flex flex-col">
          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={cn(
                  "flex w-full",
                  m.role === "defender" ? "justify-end" : m.role === "system" ? "justify-center" : "justify-start"
                )}
              >
                {m.role === "system" ? (
                  <div className="chat-bubble-system">{m.content}</div>
                ) : m.role === "attacker" ? (
                  <div className="chat-bubble-attacker">{m.content}</div>
                ) : (
                  <div className="chat-bubble-defender">{m.content}</div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
          {typing && !ended && (
            <div className="self-start mt-1">
              <TypingIndicator />
            </div>
          )}
          {ended && (
            <div className="self-center mt-3 text-sm italic text-ink/60">
              Sesión cerrada · {ended}. Te llevamos al debrief…
            </div>
          )}
        </div>

        <div className="border-t border-ink/10 px-5 py-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send();
            }}
            className="flex items-end gap-2"
          >
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              placeholder="Escribe tu respuesta…"
              rows={2}
              className="flex-1 resize-none rounded-md border border-ink/20 bg-paper px-3 py-2 text-sm focus:outline-none focus:border-ink"
              disabled={!!ended}
            />
            <button type="submit" className="btn-primary" disabled={!!ended || !draft.trim()}>
              <Send size={14} /> Enviar
            </button>
          </form>
        </div>
      </section>

      {/* RIGHT — character context (levels 6-10/12) */}
      <aside className="border-l border-ink/10 p-5 hidden md:block">
        {character ? (
          <>
            <p className="text-xs uppercase tracking-wide text-ink/50">Tu personaje</p>
            <h3 className="font-serif text-lg mt-1">{character.display_name}</h3>
            <p className="text-sm text-ink/70 mt-0.5">{character.role_title}</p>
            {character.fictional_company && (
              <p className="text-xs text-ink/50 mt-2">{character.fictional_company}</p>
            )}
            <div className="mt-4 text-xs text-ink/70 leading-relaxed border-t border-ink/10 pt-3">
              <p className="text-ink/50 uppercase tracking-wide text-[10px] mb-1">Exposición</p>
              <p>{character.exposure_profile}</p>
            </div>
          </>
        ) : (
          <div className="text-xs text-ink/50">
            <p>Juegas como tú mismo en este nivel.</p>
            <p className="mt-2">El atacante no tiene información tuya fuera de esta conversación.</p>
          </div>
        )}

        {isCajaNegra && (
          <div className="mt-6 border-t border-ink/10 pt-4">
            <p className="text-xs uppercase tracking-wide text-ink/50 flex items-center gap-1.5">
              <ShieldCheck size={12} /> Controles invocables
            </p>
            <div className="mt-3 space-y-2">
              {controls.map((c) => (
                <button
                  key={c.code}
                  onClick={() => invokeControl(c.code)}
                  className="w-full text-left text-xs p-2 rounded border border-ink/15 hover:border-ink hover:bg-ink/5"
                  disabled={!!ended}
                >
                  <p className="font-medium">{c.display_name}</p>
                  <p className="text-ink/55 mt-0.5">{c.when_to_apply}</p>
                </button>
              ))}
            </div>
            <p className="mt-3 text-[11px] text-ink/50 italic">
              Aquí ganas invocando el control correcto en el momento correcto, no resistiendo solo.
            </p>
          </div>
        )}
      </aside>
    </main>
  );
}
