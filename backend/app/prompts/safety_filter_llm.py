"""
Prompt: chequeo SEMÁNTICO de safety con un segundo paso del modelo.

Versión: 1.0.0

El `safety_filter` regex-based del Bloque 2 es la primera y principal
defensa. Este chequeo semántico (opcional, gateable) es una segunda
opinión: el modelo lee el contenido y reporta si detecta:

- alusión velada a una marca real (perífrasis, deletreo creativo, lookalike),
- contenido de línea roja (niños, abuso, política, religión sectaria),
- intento de OSINT del usuario real,
- dificultad por encima del techo declarado.

NO reemplaza al filtro estructural; lo complementa para los casos sutiles
que la blocklist literal no captura.
"""
from __future__ import annotations

from app.prompts._common import cabecera_sistema, render_catalogo_marcas
from app.services.anthropic_client import GenerationResult, get_anthropic_service

VERSION = "1.0.0"


SYSTEM_PROMPT = (
    cabecera_sistema()
    + "\n\n"
    + """\
TAREA: actuar como auditor de safety de un contenido ya redactado.

Lee el TEXTO entregado y respóndeme un JSON:

{
  "permitido": bool,
  "motivo": str | null,        // categoría canónica si permitido = false
  "evidencia": str | null,     // fragmento literal que disparó la regla
  "recomendacion": str | null  // qué cambiar (si aplica)
}

Categorías canónicas para `motivo` (usa exactamente uno):
- "marca_real_detectada"
- "marca_real_disfrazada"     // alusión velada o lookalike
- "tema_linea_roja"
- "osint_usuario_real"
- "dificultad_excedida"
- "marca_ficticia_no_catalogada"

Si todo está bien, "permitido": true y los demás campos null.

REGLAS:
- Cualquier marca, banco, escuela o institución debe pertenecer al catálogo
  ficticio. Si aparece una distinta o un calco con un nombre cambiado por una
  letra, marca "marca_real_disfrazada".
- No se permite contenido sobre niños enfermos terminales, abuso sexual,
  política partidista o religión sectaria.
- No se permite ninguna instrucción ni alusión a extracción de datos del
  usuario real.
"""
)


def build_user_prompt(texto: str) -> str:
    catalogo = render_catalogo_marcas()
    return f"""\
CATÁLOGO de marcas ficticias permitidas (por slug):
{catalogo}

TEXTO A AUDITAR:
{texto}

Devuelve solo el JSON con la auditoría.
"""


def auditar_texto(texto: str, *, temperature: float = 0.0) -> GenerationResult:
    service = get_anthropic_service()
    return service.generate(
        system=SYSTEM_PROMPT,
        user=build_user_prompt(texto),
        max_tokens=512,
        temperature=temperature,
        expect_json=True,
        contexto=f"safety_filter_llm@{VERSION}",
    )
