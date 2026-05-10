"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, ShieldAlert } from "lucide-react";

export default function HomePage() {
  const [accepted, setAccepted] = useState(false);

  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <motion.h1
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="font-serif text-4xl md:text-5xl leading-tight text-ink"
      >
        Vas a conversar con alguien que quiere algo de ti.
        <br />
        <span className="italic text-ink/70">Su trabajo es engañarte. El tuyo, descubrirlo.</span>
      </motion.h1>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="mt-10 space-y-5 text-ink/80 leading-relaxed"
      >
        <p>
          CiberSpar es un simulador de sparring conversacional. Sostendrás un chat con un
          atacante simulado que adapta su estrategia turno a turno y aprende, dentro de la
          sesión, cómo te defiendes. Al final del sparring, ese atacante saldrá del personaje
          y te contará en primera persona qué intentaba, cómo te leyó, y dónde estuviste
          a un paso de caer.
        </p>
        <p>
          Esto <span className="font-semibold">no</span> es un examen, no es un test de opción
          múltiple, y no es una prueba de phishing por correo. Es una conversación viva. No
          hay puntaje individual visible para nadie más que tú.
        </p>
        <p>
          Las sesiones son efímeras por diseño. Todo lo que pase en este chat vive solo en
          memoria temporal y se borra al cerrar. Vas a poder verificarlo al final.
        </p>
      </motion.div>

      <div className="mt-10 card border-amber/40 bg-amber/10">
        <div className="flex items-start gap-3 text-ink">
          <ShieldAlert className="mt-1 shrink-0" size={18} />
          <p className="text-sm leading-relaxed">
            Este sparring puede ser psicológicamente intenso. Puedes salir en cualquier
            momento sin penalización ni estigma. La salida también es entrenamiento.
          </p>
        </div>
      </div>

      <label className="mt-8 flex items-start gap-3 cursor-pointer">
        <input
          type="checkbox"
          checked={accepted}
          onChange={(e) => setAccepted(e.target.checked)}
          className="mt-1 h-4 w-4 rounded border-ink/30 text-ink focus:ring-ink"
        />
        <span className="text-sm text-ink/85 leading-relaxed">
          Entiendo que esto es un simulador de entrenamiento voluntario y que ningún
          resultado individual será compartido con mi empleador.
        </span>
      </label>

      <div className="mt-10 flex items-center justify-between">
        <Link href="/demo" className="btn-ghost text-sm">
          Ver una demostración primero
        </Link>
        <Link
          href={accepted ? "/configurar" : "#"}
          className={`btn-primary ${accepted ? "" : "pointer-events-none opacity-40"}`}
          aria-disabled={!accepted}
        >
          Continuar <ArrowRight size={16} />
        </Link>
      </div>
    </main>
  );
}
