"""
Enums compartidos. Listas cerradas que sostienen el marco pedagógico.

GanchoPsicologico es la "raíz" del Día Triple: los tres actos comparten
exactamente uno de estos ganchos. Cambia el disfraz, no la trampa.
"""
from enum import Enum


class Rol(str, Enum):
    """Los tres frentes del usuario-personaje a lo largo de su día."""

    CIUDADANO = "ciudadano"
    COLABORADOR = "colaborador"
    CLIENTE = "cliente"


class GanchoPsicologico(str, Enum):
    """Catálogo cerrado de ganchos psicológicos raíz."""

    URGENCIA = "urgencia"
    AUTORIDAD = "autoridad"
    MIEDO = "miedo"
    CURIOSIDAD = "curiosidad"
    RECIPROCIDAD = "reciprocidad"
    ESCASEZ = "escasez"
    PRUEBA_SOCIAL = "prueba_social"
    AFECTO = "afecto"


class Arquetipo(str, Enum):
    """Arquetipos de personaje sugeridos por el marco del cliente."""

    GUARDIAN_FINANCIERO = "guardian_financiero"
    ARQUITECTO_DIGITAL = "arquitecto_digital"
    ROSTRO_EXPERIENCIAS = "rostro_experiencias"
    CUIDADOR_FAMILIAR = "cuidador_familiar"
    EJECUTIVO_TRANSITO = "ejecutivo_transito"
    OPERADOR_CONFIANZA = "operador_confianza"


class NivelDificultad(int, Enum):
    """Solo tres niveles. Nunca hay nivel 'indistinguible'."""

    INTRODUCTORIO = 1
    INTERMEDIO = 2
    AVANZADO = 3


class CanalAtaque(str, Enum):
    """Canales por los que llega cada acto del Día Triple."""

    SMS = "sms"
    WHATSAPP = "whatsapp"
    CORREO = "correo"
    LLAMADA = "llamada"
    APP_NOTIFICACION = "app_notificacion"


class TipoIndicador(str, Enum):
    """
    Catálogo estandarizado de indicadores detectables.
    Se usan como tags en la Sala de Disección.
    """

    DOMINIO_SOSPECHOSO = "dominio_sospechoso"
    URGENCIA_ARTIFICIAL = "urgencia_artificial"
    LLAMADO_ACCION_UNICO = "llamado_accion_unico"
    AUTORIDAD_NO_VERIFICABLE = "autoridad_no_verificable"
    INCONGRUENCIA_CANAL = "incongruencia_canal"
    ERROR_CONTEXTO = "error_contexto"
    ERROR_ORTOGRAFIA = "error_ortografia"
    REMITENTE_ANOMALO = "remitente_anomalo"
    SOLICITUD_DATOS_SENSIBLES = "solicitud_datos_sensibles"
    AMENAZA_VELADA = "amenaza_velada"
    OFERTA_DESPROPORCIONADA = "oferta_desproporcionada"
    ENLACE_ACORTADO = "enlace_acortado"


class EstadoSesion(str, Enum):
    INICIADA = "iniciada"
    EN_DIA_TRIPLE = "en_dia_triple"
    EN_DISECCION = "en_diseccion"
    EN_REFLEXION = "en_reflexion"
    COMPLETADA = "completada"
