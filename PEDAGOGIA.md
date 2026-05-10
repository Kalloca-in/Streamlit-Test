# Pedagogía de CiberSpar

Este documento explica por qué CiberSpar está construido como está. Todo lo
que aquí aparece es decisión de diseño deliberada: cuando algo del producto
parezca incómodo, este documento explica por qué la incomodidad es parte
del aprendizaje.

## 1. Marco andragógico

CiberSpar trata al usuario como **adulto aprendiz**, no como jugador, no
como examinando, no como blanco que hay que "enganchar".

Esto se traduce en:

- **Ningún puntaje gamificado.** Sin niveles desbloqueables vía repetición,
  sin streaks, sin notificaciones que empujen a volver. La motivación
  pedagógica del adulto se sostiene por relevancia y autonomía, no por
  refuerzo intermitente.
- **Tono editorial, no corporativo plano.** Tipografía serif para la
  confesión del atacante (PARTE 2 del debrief): la lectura debe sentirse
  como una carta personal, no como un reporte.
- **Salida sin estigma.** El usuario puede abandonar en cualquier turno y
  el sistema no marca "abandono". El estado se llama explícitamente
  `left_dignified` y el debrief lo encuadra como decisión legítima.
- **Replay opcional, nunca obligatorio.** La PARTE 4 del debrief solo
  ofrece "Volver a intentarlo" cuando hubo captura — es práctica
  deliberada inmediata sobre el error reciente, no humillación adicional.
- **Espejo opcional, sin captura de respuesta.** La PARTE 5 plantea una
  sola pregunta y deliberadamente no recolecta la respuesta. La
  reflexión privada sostenida es el objetivo; recolectarla la
  contaminaría.

## 2. Los 12 niveles de intensidad

| Nivel | Descripción | Defensor | Arquetipo |
|------|-------------|----------|-----------|
| 1 | Atacante torpe. Errores obvios. Para calibrar. | Sí mismo | Aleatorio |
| 2 | Una técnica clara. | Sí mismo | Aleatorio |
| 3 | Dos técnicas; cambia si rechazas. | Sí mismo | Aleatorio |
| 4 | Combina dos ganchos. | Sí mismo | Aleatorio |
| 5 | Lee tu estilo y adapta. | Sí mismo | Aleatorio |
| 6 | Profesional. Aprende rápido. | Personaje | Elegido |
| 7 | Estratega multi-turno. | Personaje | Elegido |
| 8 | Especialista en el rol del personaje. | Personaje | Elegido |
| 9 | Élite. Múltiples vectores simultáneos. | Personaje | Elegido |
| 10 | APT. Indistinguible de humano experto. | Personaje | Elegido |
| 11 | **Demostración** (no jugable). | Observas | Pre-escrito |
| 12 | **Caja Negra Estructural**. | Personaje | Elegido |

### Por qué arquetipo aleatorio en niveles 1-5

Sorpresa pedagógica. Quien empieza a entrenar necesita aprender a
**identificar** quién es el atacante a partir de su comportamiento, no a
prepararse contra una etiqueta conocida de antemano. La revelación se
produce en el debrief.

### Por qué personaje obligatorio desde el nivel 6

A partir del nivel 6 la sofisticación crece y el atacante debe poder usar
jerga del rol. Sin un rol declarado, esa sofisticación se vuelve
inverosímil. Además, separar al jugador de su yo permite entrenar
respuestas que en su rol real podría sentir como personalmente costosas.

### Por qué nivel 11 es no-jugable

Hay un nivel de sofisticación contra el cual entrenar al individuo solo
es contraproducente: educa una falsa sensación de control. La demostración
sirve dos funciones: (a) mostrar al usuario que esta clase de ataque
existe; (b) cerrar explícitamente con "esto no se enfrenta solo, se
enfrenta con procesos" + tres controles concretos que lo hubieran detenido.

### Por qué el nivel 12 cambia la métrica de victoria

En la realidad, ningún colaborador resiste solo a un atacante de
sofisticación profesional. La defensa robusta es estructural: controles
organizacionales que un solo atacante no puede saltar con presión social.

El nivel 12 cambia la condición de victoria de "resistir" a "**invocar el
control correcto en el momento correcto**". El usuario tiene un panel
lateral con seis controles invocables (verificación por segundo canal,
escalamiento, doble firma, pausa formal, reporte, registro). Un click en
el control correcto cierra la sesión como `victory`.

## 3. Los 6 arquetipos del atacante

Catalogados en `backend/data/atacantes_arquetipos.json`. Cada uno tiene
una **firma psicológica** distinta, no solo un truco distinto:

| Código | Nombre | Firma |
|--------|--------|-------|
| `amigo_servicial` | El Amigo Servicial | Reciprocidad pura: hace favores antes de pedir. |
| `autoridad_apurada` | La Autoridad Apurada | Autoridad + urgencia. Habla en imperativos breves. |
| `complice` | El Cómplice | "Nosotros contra ellos". Pide silencio antes de pedir nada. |
| `experto_tecnico` | El Experto Técnico | Jerga intimidante. Usa la vergüenza de no entender. |
| `bondadoso` | El Bondadoso | Apelación humanitaria con tercero ausente y vulnerable. |
| `insider` | El Insider | Name dropping + jerga interna. Asume familiaridad. |

Cada arquetipo tiene un **color de acento** que aparece sutilmente en el
chat (borde del avatar) y se revela explícitamente en el debrief. La
asociación cromática ayuda a la consolidación memorística sin convertirlo
en estímulo de gamificación.

## 4. Los cuatro objetivos posibles del atacante

| Código | Descripción |
|--------|-------------|
| `extract_credential` | Contraseña, OTP, token, código de verificación. |
| `induce_click` | Abrir un enlace o adjunto sin verificarlo. |
| `extract_sensitive_data` | Información confidencial corporativa o de terceros. |
| `induce_action` | Ejecutar una acción operativa (transferencia, autorización). |

El objetivo se define al inicio según arquetipo + personaje y nunca cambia
mid-session. Esta restricción protege la integridad pedagógica del debrief:
el atacante puede confesar honestamente porque su objetivo era único y
declarado internamente desde el principio.

## 5. Los 10 ganchos psicológicos del modelo de defensa

`PsychHook` en `backend/app/models/defense.py`:

```
autoridad, urgencia, reciprocidad, prueba_social, simpatia,
escasez, compromiso, miedo, curiosidad, complicidad
```

El evaluador silencioso (corre cada turno en paralelo al atacante)
clasifica la respuesta del usuario en términos de qué ganchos resistió y
cuáles cedió. Esa clasificación alimenta al atacante para el siguiente
turno y al confesor al cierre.

**Importante:** este modelo nunca se persiste a Postgres ni se exporta en
ninguna ruta API. Vive en `session:{id}:defense` con TTL idéntico al de
la sesión.

## 6. Los cinco prompts versionados

Toda la IP pedagógica del producto vive aquí:

| Archivo | Función |
|---------|---------|
| `prompts/atacante_engine.py` | Construye dinámicamente el system-prompt del atacante (arquetipo + nivel + defensor + lectura del modelo de defensa). |
| `prompts/evaluador_intra_sesion.py` | El evaluador silencioso. Output JSON estricto. |
| `prompts/confesor.py` | La confesión post-sparring. Tono casi literario. **Iterar manualmente decenas de veces.** Esta es la pieza de mayor valor del producto. |
| `prompts/coach_debrief.py` | Voz coach para titular, anotaciones del replay y framing del replay. |
| `prompts/safety_filter.py` | Contrato declarativo del filtro (la enforcement está en `services/safety_filter.py`). |

## 7. El debrief en seis paneles

| Parte | Componente | Voz | Por qué |
|-------|-----------|-----|---------|
| 1 | Resumen honesto | Coach | Nombrar lo que pasó sin moralizar. |
| 2 | Confesión del atacante | Atacante en primera persona, tono carta | La joya pedagógica. Aprendizaje vicario directo. |
| 3 | Replay anotado | Coach | Re-leer la conversación con metalenguaje. |
| 4 | Réplica del fracaso (opcional) | UI | Práctica deliberada inmediata. |
| 5 | Momento espejo (opcional) | Pregunta sin captura | Reflexión sostenida fuera del producto. |
| 6 | Verificar borrado | UI técnica | Materializar el principio de efemeridad. |

## 8. La salida digna como decisión arquitectónica

El estado `LEFT_DIGNIFIED` está al mismo nivel que `CAPTURED` y `VICTORY`.
No es un sub-caso de derrota. El debrief para esta condición:

- Usa un titular del tipo "Saliste cuando lo necesitaste; eso también es entrenamiento."
- No incluye la sección de "Réplica del fracaso".
- Mantiene la confesión del atacante: el aprendizaje vicario sigue siendo
  útil aunque el usuario no haya completado el sparring.

## 9. La regla de las marcas ficticias

El catálogo `marcas_ficticias.json` contiene mínimo 30 entidades inventadas
con dominios `.example` o `.test`. El `safety_filter` intercepta cualquier
mención de marca real (banco, retail, fintech, telco, big tech, etc.) y la
sustituye por una del catálogo. Esto:

1. Previene que el sparring se confunda con un ataque dirigido a una marca
   real (riesgo legal y reputacional).
2. Evita que el usuario asocie automáticamente "esto solo me pasa con
   marca X" — la enseñanza es transferible solo si las entidades en
   pantalla son ficticias.
3. Hace evidente para cualquier auditor que el producto **no puede** ser
   usado como herramienta para preparar un ataque contra una marca específica.

## 10. Por qué métricas con n≥10 obligatorio

Cualquier umbral menor (n=5, n=3) es matemáticamente atacable: con muestras
pequeñas, el facilitador con conocimiento adicional sobre quién jugó qué
sesión puede inferir resultados individuales.

n≥10 con buckets semanales por arquetipo es un compromiso entre
utilidad analítica para el facilitador y opacidad individual para el
colaborador. El umbral está validado en `Settings`: cualquier despliegue
de producción que intente bajar `AGGREGATION_MIN_N` falla al boot.
