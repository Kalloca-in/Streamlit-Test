# Plataforma de Awareness

Plataforma local para que equipos de seguridad y proveedores de servicios de
awareness preparen campañas de phishing simulado contra colaboradores de
una organización **con autorización contractual previa**.

## Qué hace

- Permite declarar el alcance corporativo del engagement (cliente, sector,
  dominio sandbox controlado, departamentos, vigencia).
- Asistente IA conversacional para planificar temáticas (Fase 2).
- Genera plantillas de phishing simulado calibradas a roles corporativos
  genéricos, no a individuos nombrados (Fase 2).
- Exporta paquetes para alimentar herramientas de envío del cliente
  (GoPhish, KnowBe4, Defender) (Fase 3).
- Registra metadata de cada generación (operador, config, tokens) en
  `logs/generations.jsonl`. **Nunca** registra el contenido generado.

## Qué NO hace

- **No envía** correos, SMS, WhatsApp ni mensajes de ningún tipo.
- **No genera ataques personalizados** contra individuos nombrados.
- **No construye dossiers OSINT** sobre objetivos específicos.
- **No suplanta marcas, bancos, escuelas ni instituciones** públicas reales.
- **No targetea contextos personales** (familia, hijos, salud, finanzas
  personales) — esto está bloqueado por defecto y no se puede desactivar.

## Estado actual

Fase 1 — Esqueleto, acceso de operador, gate legal y alcance corporativo.

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

## Variables de entorno

| Variable            | Descripción                                              |
|---------------------|----------------------------------------------------------|
| `ANTHROPIC_API_KEY` | Clave del API de Anthropic.                              |
| `MODEL_NAME`        | Modelo Claude (default: `claude-opus-4-7`).             |
| `OPERATOR_PASSWORD` | Contraseña local que el operador debe ingresar.          |
| `APP_VERSION`       | Versión mostrada en el footer.                           |

## Arquitectura

```
app.py                    # Entrypoint Streamlit + máquina de estados
src/
  llm.py                  # Cliente Anthropic centralizado (caching, errores)
  state.py                # Helpers de session_state
  sections/
    login.py              # Acceso de operador
    acuerdo.py            # Gate de uso responsable
    alcance.py            # Alcance corporativo
    planificacion.py      # (Fase 2) Asistente IA de planificación
  prompts/                # (Fase 2) System prompts versionados
  exporters/              # (Fase 3) Exportadores GoPhish/HTML/PDF
catalog/                  # (Fase 2) Plantillas curadas baseline
logs/generations.jsonl    # Auditoría de generaciones (sin contenido)
```

## Marco legal

Esta plataforma es una herramienta. La autorización legal para correr
simulaciones de phishing contra los colaboradores de una organización
**debe estar formalizada por escrito** entre el cliente final y el
operador, antes de cualquier uso. Ver `LEGAL.md` (próximo) para una
plantilla sugerida de cláusula contractual.

El uso no autorizado contra terceros es ilegal en la mayoría de las
jurisdicciones.
