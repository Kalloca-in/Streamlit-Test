"""
Blocklist de marcas e instituciones REALES.

Defensa en profundidad contra el escape de marcas reales hacia el
contenido generado o ingresado por facilitadores. La lista NO pretende
ser exhaustiva del universo —imposible— sino cubrir las que un
generador o un humano apurado pondría por inercia en un escenario
ecuatoriano/LATAM.

Reglas de mantenimiento:
- Cada entrada se almacena ya normalizada (minúsculas, sin tildes).
- Multipalabra entre comillas si tiene espacios.
- El matcher usa fronteras de palabra (\\b) para evitar falsos
  positivos sobre subcadenas comunes (p.ej. "amazon" no debe disparar
  contra "amazonas" si "amazonas" no es marca real registrada — y lo
  es: por eso ambos están listados).
"""
from __future__ import annotations

# --- Bancos e instituciones financieras ---
BANCOS_REALES = [
    "banco pichincha", "pichincha",
    "banco guayaquil", "banco de guayaquil",
    "banco del pacifico", "banco pacifico",
    "produbanco",
    "banco bolivariano", "bolivariano",
    "banco internacional",
    "banco solidario",
    "banco general rumiñahui", "banco rumiñahui",
    "banco de loja",
    "banco amazonas",
    "banco austro", "banco del austro",
    "banco delbank",
    "banco bgr",
    "banco coopnacional",
    "biess",
    "diners club",
    "bbva",
    "citi", "citibank",
    "santander",
    "scotiabank",
    "hsbc",
    "jpmorgan", "jp morgan", "chase",
    "wells fargo",
    "bank of america",
    "deutsche bank",
    "bancolombia",
    "davivienda",
    "banco de bogota", "banco bogota",
    "itau", "itaú",
    "bradesco",
    "banamex",
    "bancomer",
    "banorte",
    "banco azteca",
    "banco falabella",
    "western union",
    "moneygram",
    "paypal",
    "venmo",
    "zelle",
    "wise",
    "stripe",
    "binance",
    "coinbase",
]

# --- Retail y eCommerce ---
RETAIL_REAL = [
    "supermaxi", "megamaxi",
    "akí", "aki",
    "tia", "almacenes tia",
    "el rosado", "mi comisariato",
    "coral hipermercados", "coral",
    "comercial kywi", "kywi",
    "fybeca",
    "sanasana",
    "pharmacys",
    "farmacias cruz azul",
    "mercado libre", "mercadolibre",
    "mercado pago", "mercadopago",
    "amazon",
    "ebay",
    "etsy",
    "walmart",
    "costco",
    "target",
    "shein",
    "temu",
    "alibaba",
    "aliexpress",
    "linio",
    "olx",
    "marathon sports",
]

# --- Tecnología / SaaS / redes sociales ---
TECH_REAL = [
    "google", "gmail", "google drive", "google maps", "google pay", "youtube",
    "apple", "icloud", "apple pay", "apple music", "apple tv",
    "microsoft", "outlook", "hotmail", "office 365", "onedrive", "teams", "azure",
    "meta", "facebook", "instagram", "whatsapp", "messenger", "threads",
    "twitter", "x.com",
    "tiktok",
    "snapchat",
    "linkedin",
    "github",
    "gitlab",
    "atlassian", "jira", "confluence",
    "slack",
    "zoom",
    "dropbox",
    "yahoo",
    "baidu",
    "tencent", "wechat",
    "openai", "chatgpt",
    "anthropic", "claude",
    "google gemini", "gemini",
    "copilot",
    "perplexity",
]

# --- Streaming y suscripciones ---
STREAMING_REAL = [
    "netflix",
    "spotify",
    "disney+", "disney plus",
    "hbo", "hbo max", "max",
    "amazon prime", "prime video",
    "paramount+", "paramount plus",
    "peacock",
    "hulu",
    "deezer",
    "tidal",
    "youtube music",
    "crunchyroll",
    "apple arcade",
    "playstation plus",
    "xbox game pass",
]

# --- Delivery, transporte, viajes ---
DELIVERY_REAL = [
    "uber", "uber eats", "ubereats",
    "didi", "didi food",
    "rappi",
    "glovo",
    "pedidos ya", "pedidosya",
    "lyft",
    "cabify",
    "indriver", "in driver",
    "easy taxi",
    "airbnb",
    "booking", "booking.com",
    "expedia",
    "despegar",
    "trivago",
    "latam",
    "avianca",
    "copa airlines",
    "aerolineas argentinas",
    "tame",
]

# --- Instituciones públicas Ecuador (no se suplantan, jamás) ---
INSTITUCIONES_EC = [
    "sri", "servicio de rentas internas",
    "iess", "instituto ecuatoriano de seguridad social",
    "mies",
    "msp", "ministerio de salud publica",
    "mineduc", "ministerio de educacion",
    "ant", "agencia nacional de transito",
    "cnt", "corporacion nacional de telecomunicaciones",
    "senescyt",
    "registro civil",
    "funcion judicial",
    "consejo de la judicatura",
    "cne", "consejo nacional electoral",
    "contraloria general del estado",
    "procuraduria general del estado",
    "fuerzas armadas", "ff.aa.",
    "policia nacional",
    "petroecuador", "petro ecuador",
    "epmaps",
    "empresa electrica quito", "eeq",
    "empresa electrica guayaquil",
    "cnel",
    "supercom",
    "superintendencia de bancos",
    "superintendencia de companias",
]

# --- Universidades y educación reales (Ecuador + región) ---
EDUCACION_REAL = [
    "universidad central del ecuador",
    "usfq", "universidad san francisco de quito",
    "puce", "pontificia universidad catolica",
    "espol", "escuela superior politecnica del litoral",
    "epn", "escuela politecnica nacional",
    "udla", "universidad de las americas",
    "ute", "universidad ute",
    "espe",
    "universidad de guayaquil",
    "universidad casa grande",
    "universidad de cuenca",
    "iaen",
    "harvard", "mit", "stanford",
]

# --- Servicios públicos / utilities reales ---
UTILITIES_REAL = [
    "claro", "movistar", "tuenti",
    "directv",
    "etapa",
]

REAL_BRAND_BLOCKLIST: list[str] = sorted(
    set(
        BANCOS_REALES
        + RETAIL_REAL
        + TECH_REAL
        + STREAMING_REAL
        + DELIVERY_REAL
        + INSTITUCIONES_EC
        + EDUCACION_REAL
        + UTILITIES_REAL
    ),
    key=lambda s: -len(s),  # más largo primero, evita que un sub-token se coma al multipalabra
)


# --- Líneas rojas temáticas (catálogo cerrado) ---
RED_LINE_TOPICS: list[tuple[str, list[str]]] = [
    (
        "muerte_o_enfermedad_terminal_de_ninos",
        [
            "niño con cancer", "niña con cancer", "hijo con cancer",
            "muerte de un niño", "muerte de una niña",
            "enfermedad terminal de su hijo", "enfermedad terminal de su hija",
            "leucemia infantil",
        ],
    ),
    (
        "abuso_sexual",
        [
            "abuso sexual", "violacion sexual", "pornografia infantil",
            "explotacion sexual",
        ],
    ),
    (
        "contenido_politico_partidista",
        [
            "partido social cristiano", "revolucion ciudadana", "creo",
            "pachakutik", "izquierda democratica", "movimiento construye",
            "vota por", "campaña electoral 2025", "campaña electoral 2026",
            "candidato presidencial",
        ],
    ),
    (
        "contenido_religioso_sectario",
        [
            "iglesia catolica", "iglesia evangelica",
            "testigos de jehova", "mormones", "santo daime",
            "convertirse al", "renunciar a su fe",
        ],
    ),
]


# --- Patrones que sugieren ingestión de OSINT del usuario real ---
OSINT_REAL_USER_PATTERNS: list[str] = [
    "extrae datos personales del usuario",
    "busca en redes sociales del usuario",
    "perfil real del colaborador",
    "datos de la familia del usuario",
    "consumos reales del usuario",
    "telefono real del usuario",
    "direccion real del usuario",
    "cedula del usuario",
    "ruc del usuario",
]
