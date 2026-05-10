# Plataforma de Awareness

Plataforma local en Streamlit para que equipos de seguridad y proveedores
de servicios de awareness preparen campañas de phishing simulado contra
colaboradores de una organización **con autorización contractual previa**.

La plataforma usa Anthropic Claude detrás para asistir la planificación,
generar plantillas calibradas al contexto corporativo y validar que cada
generación se mantenga dentro del scope autorizado.

## Qué hace

- **Acceso de operador** con identificación (nombre + cliente + folio
  contractual) registrada en log de auditoría.
- **Gate de uso responsable** con cuatro declaraciones explícitas que el
  operador debe aceptar antes de cualquier acción.
- **Captura de alcance corporativo**: cliente, sector, tamaño, dominio
  sandbox controlado, departamentos, vigencia y temáticas vetadas.
- **Asistente de planificación IA**: dos modos —
  - "Tengo plan del cliente": pegás el plan mensual y el asistente lo
    estructura en una lista de temas.
  - "Necesito propuestas": el asistente propone 6-8 temas según alcance
    y amenazas vigentes.
- **Generación de plantillas** por (tema, vector, dificultad) con safety
  filter pre-generación de dos capas (hard rules + filtro semántico LLM).
- **Exportación** a un ZIP que incluye GoPhish JSON, HTMLs por plantilla,
  y un PDF brief para el equipo de seguridad y el debrief.
- **Logging metadata-only** de cada generación en `logs/generations.jsonl`
  (operador hashed, config, tokens consumidos). **Nunca** se registra el
  contenido generado ni los textos del operador.

## Qué NO hace

- **No envía** correos, SMS, WhatsApp ni mensajes de ningún tipo. La
  plataforma prepara contenido para que se envíe desde la infraestructura
  autorizada del cliente (GoPhish, KnowBe4, Microsoft Defender, etc.).
- **No genera ataques personalizados** contra individuos nombrados. Las
  plantillas se calibran a roles corporativos genéricos.
- **No construye dossiers OSINT** sobre objetivos específicos.
- **No suplanta marcas, bancos, escuelas ni instituciones** públicas reales.
  El dominio remitente siempre es el sandbox declarado por el operador.
- **No targetea contextos personales** (familia, hijos, salud, finanzas
  personales) — bloqueado por hard rule, no se puede desactivar.
- **No persiste dossiers ni contenido generado** más allá de la sesión
  activa. Los exports se generan en memoria y se descargan; nada queda
  en disco salvo metadata de auditoría.

## Cómo correr local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env: ANTHROPIC_API_KEY y OPERATOR_PASSWORD
streamlit run app.py
```

Abrir http://localhost:8501.

## Cómo correr con Docker

```bash
docker build -t plataforma-awareness .
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e OPERATOR_PASSWORD=... \
  -v $(pwd)/logs:/app/logs \
  plataforma-awareness
```

El volumen `logs/` permite persistir el log de auditoría fuera del
contenedor.

## Variables de entorno

| Variable            | Descripción                                              |
|---------------------|----------------------------------------------------------|
| `ANTHROPIC_API_KEY` | Clave del API de Anthropic.                              |
| `MODEL_NAME`        | Modelo Claude (default: `claude-opus-4-7`).              |
| `OPERATOR_PASSWORD` | Contraseña local que el operador debe ingresar.          |
| `APP_VERSION`       | Versión mostrada en el footer.                           |

## Tests

```bash
pip install pytest
pytest -v
```

Los tests cubren:
- `tests/test_safety_hard_rules.py`: las reglas deterministas del safety
  filter (las que NO dependen del LLM).
- `tests/test_exporters.py`: que los exports tienen todos los artefactos,
  el manifest no filtra contenido, los placeholders de tracking se
  sustituyen correctamente, y el dominio sandbox se respeta.

No hay tests para los prompts del sistema porque dependerían del modelo
en vivo. Si querés pruebas de regresión sobre los prompts, ejecutá un
golden-set manual contra el endpoint real.

## Arquitectura

```
app.py                       # Entrypoint Streamlit + máquina de estados
src/
  llm.py                     # Cliente Anthropic centralizado (caching, errores, structured outputs)
  state.py                   # Helpers de session_state
  safety.py                  # Hard rules + invocación del LLM filter
  prompts/                   # System prompts versionados (la IP del producto)
    campaign_planner.py      # Estructura plan mensual del cliente
    topic_proposer.py        # Propone temas según amenazas vigentes
    template_generator.py    # Genera plantilla calibrada
    safety_filter.py         # Filtro semántico pre-generación
  sections/                  # Renderers de cada paso de la UI
    login.py
    acuerdo.py
    alcance.py
    planificacion.py
    generacion.py
    exportacion.py
  exporters/                 # Formatos de salida
    gophish.py               # JSON importable en GoPhish
    html_pkg.py              # HTMLs standalone (email + landing)
    pdf_brief.py             # PDF brief con todas las plantillas
    bundle.py                # ZIP con todo
tests/                       # pytest
catalog/                     # Reservado para temas curados (no usado en MVP)
logs/generations.jsonl       # Auditoría metadata-only
LEGAL.md                     # Cláusula contractual sugerida
Dockerfile
```

## Decisiones de diseño que sostienen la seguridad

Estas no son convenciones, son la diferencia entre una herramienta
defensiva y un kit ofensivo:

1. **El dominio remitente es siempre el sandbox declarado.** El generador
   nunca propone dominios look-alike de marcas reales. Esto es una
   estructura de detección estructural: cualquier colaborador que pase
   el cursor sobre el remitente ve que no es el dominio corporativo
   real, y eso es exactamente lo que el debrief enseña.

2. **Los niveles de dificultad están framed como tiers educativos, no
   como tiers de eficacia.** Tier 3 explícitamente NO es
   "indistinguible". Es "requiere verificación por canal alternativo".
   El generador siempre incluye al menos un indicador detectable.

3. **Safety filter de dos capas.** Hard rules deterministas primero
   (cubren los casos donde no queremos depender del juicio del modelo),
   filtro semántico LLM después (cubre las combinaciones contextuales
   que las reglas pueden dejar pasar).

4. **No targeting individual.** No hay campo "objetivo" con nombre,
   cargo, empresa específica. Las plantillas se calibran a roles
   genéricos del cliente.

5. **No vectores fuera del perímetro corporativo.** Email, SMS y
   Microsoft Teams. No WhatsApp (canal personal), no scripts de
   llamada (vishing requiere setup operacional fuera de scope).

6. **Logging metadata-only.** El log audita actividad sin persistir
   contenido. Si el sistema se compromete, no se filtra material
   ofensivo.

## Marco legal

Ver [LEGAL.md](./LEGAL.md) para una plantilla sugerida de cláusula
contractual y referencias regulatorias por jurisdicción.

La aceptación del acuerdo dentro de la app es **auto-atestación**: no
verifica el contrato. La autorización legal real debe estar formalizada
por escrito entre el cliente final y el operador, antes de cualquier
uso. El uso no autorizado contra terceros es ilegal en la mayoría de
las jurisdicciones.
