import Link from "next/link";

export default function Landing() {
  return (
    <div className="max-w-4xl mx-auto px-6 pt-20 pb-24">
      <p className="text-xs uppercase tracking-[0.3em] text-accent mb-6">CiberTeatro</p>

      <h1 className="serif text-5xl md:text-6xl leading-tight">
        Hoy no aprenderás sobre ciberseguridad.
        <br />
        Vas a vivirla a través de alguien más.
      </h1>

      <p className="mt-8 text-lg text-ink/80 max-w-2xl">
        Eliges un personaje ficticio. Sigues su día. Recibe tres ataques en tres roles
        distintos: como ciudadano, como colaborador y como cliente. Tú observas, decides
        e intervienes. Al final ves cómo se construyó la trampa, y por qué la misma
        persona —tú— es la superficie de ataque en los tres frentes.
      </p>

      <div className="mt-10 flex flex-wrap gap-3">
        <Link href="/personajes" className="btn-primary">
          Elegir personaje
        </Link>
        <Link href="/biblioteca" className="btn-ghost">
          Explorar la biblioteca
        </Link>
      </div>

      <hr className="my-16 border-white/5" />

      <div className="grid md:grid-cols-3 gap-6">
        <div className="card">
          <div className="text-sm text-muted mb-1">Acto 1 · 07:30</div>
          <div className="role-pill role-pill--ciudadano mb-3">Ciudadano</div>
          <p className="text-sm text-ink/85">
            Antes de salir, entra un mensaje. ¿Su banco? ¿El colegio de su hijo? ¿Una
            multa? La urgencia decide por nosotros si no nos detenemos.
          </p>
        </div>
        <div className="card">
          <div className="text-sm text-muted mb-1">Acto 2 · 11:00</div>
          <div className="role-pill role-pill--colaborador mb-3">Colaborador</div>
          <p className="text-sm text-ink/85">
            Mediodía en su empresa ficticia. Un correo del &quot;jefe&quot;. Un favor con plazo. La
            misma trampa con otro disfraz.
          </p>
        </div>
        <div className="card">
          <div className="text-sm text-muted mb-1">Acto 3 · 19:00</div>
          <div className="role-pill role-pill--cliente mb-3">Cliente</div>
          <p className="text-sm text-ink/85">
            Llega a casa, abre el chat. Otra notificación, otra promesa, otro plazo. Tres
            disfraces, un solo gancho.
          </p>
        </div>
      </div>

      <div className="mt-16 text-xs text-muted leading-relaxed">
        <strong className="text-ink/80">Compromisos no negociables.</strong> Nunca te
        atacamos a ti. No procesamos tus redes ni tus consumos. Ningún personaje, marca,
        banco o institución que verás existe en la realidad. La dificultad está acotada:
        siempre hay algo aprendible. Tu reflexión personal nunca se comparte
        individualizada con tu empleador.
      </div>
    </div>
  );
}
