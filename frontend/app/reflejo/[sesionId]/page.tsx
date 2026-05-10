"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { Rol } from "@/lib/types";
import { rolLabel } from "@/lib/utils";

export default function ReflejoPage() {
  const { sesionId } = useParams<{ sesionId: string }>();
  const router = useRouter();
  const [rol, setRol] = useState<Rol | "">("");
  const [eco, setEco] = useState("");
  const [cambio, setCambio] = useState("");
  const [confianza, setConfianza] = useState<number>(3);
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function enviar() {
    if (!sesionId) return;
    setEnviando(true);
    setErr(null);
    try {
      await api.registrarReflexion(sesionId, {
        rol_mas_vulnerable: (rol || null) as Rol | null,
        eco_personal: eco || null,
        cambio_propuesto: cambio || null,
        nivel_confianza: confianza,
      });
      setEnviado(true);
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setEnviando(false);
    }
  }

  if (enviado) {
    return (
      <div className="max-w-2xl mx-auto px-6 pt-16 pb-24">
        <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">Mi Reflejo</p>
        <h1 className="serif text-4xl mb-3">Guardado.</h1>
        <p className="text-ink/85">
          Tu respuesta es privada y queda asociada solo a tu progreso. Tu empleador
          nunca verá respuestas individuales: cualquier reporte se entrega agregado y
          anónimo, con un mínimo de respuestas para preservar tu identidad.
        </p>
        <div className="mt-8 flex gap-3">
          <button className="btn-primary" onClick={() => router.push("/dashboard")}>
            Ver mi progreso
          </button>
          <button className="btn-ghost" onClick={() => router.push("/biblioteca")}>
            Otro caso
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-6 pt-12 pb-24">
      <p className="text-xs uppercase tracking-[0.3em] text-accent mb-3">Mi Reflejo</p>
      <h1 className="serif text-3xl md:text-4xl">No es examen. Es espejo.</h1>
      <p className="mt-3 text-ink/75">
        Tres preguntas cortas. Tus respuestas son privadas y solo alimentan tu propio
        dashboard de progreso.
      </p>

      <div className="mt-10 space-y-7">
        <Pregunta titulo="¿En cuál de los tres roles te sentiste más cerca de caer si fueras tú?">
          <div className="flex gap-3 flex-wrap">
            {(["ciudadano", "colaborador", "cliente"] as Rol[]).map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRol(r)}
                className={`role-pill role-pill--${r} ${rol === r ? "ring-2 ring-accent" : ""}`}
              >
                {rolLabel[r]}
              </button>
            ))}
          </div>
        </Pregunta>

        <Pregunta titulo="¿Qué del comportamiento del personaje reconociste en ti mismo?">
          <textarea
            rows={4}
            value={eco}
            onChange={(e) => setEco(e.target.value)}
            className="w-full bg-paper border border-white/10 rounded-xl p-3 text-sm"
            placeholder="Sin presiones — escribe libremente."
          />
        </Pregunta>

        <Pregunta titulo="¿Qué cambiarías mañana en tu propia rutina?">
          <textarea
            rows={3}
            value={cambio}
            onChange={(e) => setCambio(e.target.value)}
            className="w-full bg-paper border border-white/10 rounded-xl p-3 text-sm"
            placeholder="Una acción concreta es suficiente."
          />
        </Pregunta>

        <Pregunta titulo="¿Qué tan confiado/a sales hoy?">
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setConfianza(n)}
                className={`w-10 h-10 rounded-full border ${
                  confianza === n
                    ? "bg-accent text-background border-accent"
                    : "border-white/10 text-ink/85 hover:border-white/30"
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        </Pregunta>
      </div>

      {err && <p className="text-danger mt-4 text-sm">{err}</p>}

      <div className="mt-10 flex gap-3">
        <button onClick={enviar} disabled={enviando} className="btn-primary disabled:opacity-50">
          {enviando ? "Guardando…" : "Guardar reflexión"}
        </button>
      </div>
    </div>
  );
}

function Pregunta({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="serif text-lg mb-3">{titulo}</h3>
      {children}
    </div>
  );
}
