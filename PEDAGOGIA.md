# PEDAGOGIA · Marco didáctico de CiberTeatro

Este documento explica **qué está comprando el cliente** cuando contrata la
plataforma. Es la lectura mínima para responsables de awareness, equipos de
people analytics y comités de seguridad.

---

## 1. Premisa

La mayoría de los programas de awareness corporativos enseñan a un colaborador
cómo no caer **dentro** de la oficina: phishing del CEO, BEC, descargas
maliciosas. Eso cubre, en el mejor caso, **un tercio** de su superficie real
de ataque.

CiberTeatro asume que el colaborador es la misma persona en tres roles:

- **Ciudadano** — recibe ataques en su vida personal (banca, salud, educación
  de sus hijos, multas, servicios).
- **Colaborador** — recibe ataques contra su rol corporativo (BEC, fraude del
  CEO, suplantación de RR.HH., proveedores).
- **Cliente** — recibe ataques contra su consumo (streaming, retail,
  delivery, telco).

Los atacantes saben que es la misma persona. Los programas de awareness no.

---

## 2. El gancho psicológico raíz

Cada Día Triple se construye sobre **un único gancho psicológico raíz**, del
catálogo cerrado:

| Gancho | Cómo opera |
|--------|------------|
| **Urgencia** | Plazo artificial — "antes de las 11pm". Anula la verificación. |
| **Autoridad** | Apela a una jerarquía no verificable — "el CFO necesita". |
| **Miedo** | Activa el cuerpo antes que el pensamiento — "tu hijo, una multa". |
| **Curiosidad** | "Recibo inesperado, repo con tu nombre". Mueve el clic reflejo. |
| **Reciprocidad** | "Te hicieron un favor / un descuento / un bono". Crea deuda falsa. |
| **Escasez** | "Solo quedan 3 cupos". Empuja a decidir sin comparar. |
| **Prueba social** | "Tus colegas ya respondieron". Asume seguridad de la mayoría. |
| **Afecto** | Apela a un vínculo simulado. Romance scams, peticiones íntimas. |

**Diseño pedagógico clave:** los tres actos del Día Triple usan el **mismo
gancho** con tres disfraces distintos. El usuario, que vio el primer acto
inocentemente, experimenta el "click" cuando reconoce la estructura repetida
en el segundo y el tercero.

---

## 3. Estructura del Día Triple

```
07:30  ACTO 1 — CIUDADANO   →   SMS / chat / app pública
                                Marca ficticia del catálogo (banco / utility)

11:00  ACTO 2 — COLABORADOR →   Correo o canal interno
                                Empresa ficticia (catálogo de empleadores)

19:00  ACTO 3 — CLIENTE     →   Mensajería / app
                                Marca de consumo del catálogo (retail / streaming)
```

Cada acto entrega:

1. **Un mensaje dramatizado** con render fiel al canal (UI de SMS, de chat, de
   correo).
2. **3 a 6 indicadores detectables** del catálogo cerrado.
3. **3 o 4 opciones de decisión**, al menos una segura.
4. **Consecuencia explícita** de cada decisión.

Tras los tres actos, viene la **revelación**: una pantalla que nombra el gancho
raíz y articula por qué los tres compartían estructura. Es el golpe pedagógico.

---

## 4. Catálogo de indicadores

Estandarizado y cerrado para que el aprendizaje sea acumulativo entre casos:

- Dominio sospechoso
- Urgencia artificial
- Llamado a acción único
- Autoridad no verificable
- Incongruencia de canal
- Error de contexto
- Error de ortografía
- Remitente anómalo
- Solicitud de datos sensibles
- Amenaza velada
- Oferta desproporcionada
- Enlace acortado

Cada indicador en la base tiene `tipo`, `fragmento` (texto literal a resaltar)
y `explicacion` (1–2 frases en lenguaje llano, sin jerga).

---

## 5. La Sala de Disección

Tras vivir el día, el usuario puede entrar a la "Sala de Disección" donde:

- Cada mensaje se muestra con sus fragmentos resaltados.
- Al pasar el cursor, aparece la explicación didáctica.
- Hay una vista de **intersección**: qué indicadores se repitieron en los tres
  actos. Esto cierra el bucle pedagógico: el patrón es lo que el usuario
  aprende, no las marcas concretas.

---

## 6. Mi Reflejo (auto-evaluación reflexiva)

**No es examen.** Cuatro preguntas cortas:

1. ¿En cuál de los tres roles te sentiste más cerca de caer?
2. ¿Qué del comportamiento del personaje reconociste en ti mismo?
3. ¿Qué cambiarías mañana en tu propia rutina?
4. ¿Qué tan confiado/a sales hoy? (1–5)

Las respuestas son **estrictamente privadas** por usuario. Alimentan el
dashboard personal. **El empleador nunca ve respuestas individuales.**

---

## 7. Reportes al cliente

Al facilitador (operador de awareness del cliente) se le entregan **solo
reportes agregados**, con:

- Un mínimo de respuestas configurable (por defecto `MIN_AGGREGATE_N = 10`).
  Por debajo de ese umbral, la plataforma **se niega a mostrar métricas**.
- Métricas: tasa de decisiones seguras global, tasa por rol, número de
  sesiones completadas, número de reflexiones.
- Sin descender nunca a una respuesta individual identificable.

Esto es regla de producto, no opción configurable a la baja.

---

## 8. Curva de aprendizaje

Recomendación operativa para el cliente:

| Mes | Foco | Niveles |
|-----|------|---------|
| 1 | **Reconocer** — los 3 ganchos más frecuentes (urgencia, autoridad, miedo) | 1 |
| 2 | **Discriminar** — ganchos sutiles (curiosidad, reciprocidad, prueba social) | 2 |
| 3 | **Cruzar roles** — el mismo usuario juega tres personajes con tres ganchos | 2-3 |
| 4+ | **Casos del mes** curados por el equipo de awareness del cliente | 2-3 |

Nivel 4 **no existe**. La promesa es detección, no captura.

---

## 9. Lo que NO entrega esta plataforma

- No envía correos / SMS / mensajes a destinatarios reales. No es una
  plataforma de phishing simulado.
- No mide al colaborador individualizadamente para su empleador.
- No procesa OSINT del usuario real ni de su entorno.
- No produce contenido sobre niños enfermos terminales, abuso sexual,
  contenido político partidista o religioso sectario.
- No genera dificultad por encima de 3.

Cada uno de estos límites está codificado. No son lineamientos: son código.
