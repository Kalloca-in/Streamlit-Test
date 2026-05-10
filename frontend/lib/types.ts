// Tipos espejo del backend. Solo lo que la UI consume.

export type Rol = "ciudadano" | "colaborador" | "cliente";
export type Canal = "sms" | "whatsapp" | "correo" | "llamada" | "app_notificacion";
export type GanchoPsicologico =
  | "urgencia" | "autoridad" | "miedo" | "curiosidad"
  | "reciprocidad" | "escasez" | "prueba_social" | "afecto";
export type Arquetipo =
  | "guardian_financiero" | "arquitecto_digital" | "rostro_experiencias"
  | "cuidador_familiar" | "ejecutivo_transito" | "operador_confianza";
export type TipoIndicador =
  | "dominio_sospechoso" | "urgencia_artificial" | "llamado_accion_unico"
  | "autoridad_no_verificable" | "incongruencia_canal" | "error_contexto"
  | "error_ortografia" | "remitente_anomalo" | "solicitud_datos_sensibles"
  | "amenaza_velada" | "oferta_desproporcionada" | "enlace_acortado";

export interface VectorExposicion {
  redes: string[];
  rutinas: string[];
  consumos: string[];
}

export interface Personaje {
  id: string;
  nombre: string;
  edad: number;
  arquetipo: Arquetipo;
  nivel_sugerido: number;
  cargo_ficticio: string;
  empresa_ficticia: string;
  contexto_familiar: string;
  habitos_consumo: string;
  vector_exposicion: VectorExposicion;
  marcas_asociadas: string[];
  avatar_url: string | null;
  disclaimer_visible: boolean;
  es_semilla: boolean;
}

export interface OpcionDecision {
  id: string;
  texto: string;
  consecuencia: string;
  es_segura: boolean;
}

export interface Indicador {
  id: string;
  tipo: TipoIndicador;
  fragmento: string;
  explicacion: string;
}

export interface Acto {
  id: string;
  orden: number;
  rol: Rol;
  canal: Canal;
  hora_dramatizada: string;
  remitente_aparente: string;
  asunto: string | null;
  cuerpo: string;
  marca_ficticia_slug: string | null;
  opciones_decision: OpcionDecision[];
  indicadores: Indicador[];
}

export interface DiaTriple {
  id: string;
  personaje_id: string;
  titulo: string;
  gancho_psicologico_raiz: GanchoPsicologico;
  nivel_dificultad: number;
  nota_revelacion: string;
  actos: Acto[];
}

export interface MarcaFicticia {
  slug: string;
  nombre: string;
  sector: string;
  dominio: string;
  logo_placeholder: string;
  descripcion: string;
}

export interface Sesion {
  id: string;
  usuario_id: string;
  personaje_id: string;
  dia_triple_id: string;
  estado: string;
  iniciada_en: string | null;
  completada_en: string | null;
}

export interface Decision {
  id: string;
  acto_id: string;
  rol: Rol;
  opcion_elegida: string;
  fue_segura: boolean;
  indicadores_detectados: string[];
}

export interface ProgresoUsuario {
  sesiones_iniciadas: number;
  sesiones_completadas: number;
  decisiones_totales: number;
  decisiones_seguras: number;
  por_rol: Record<Rol, { total: number; seguras: number }>;
}

export interface ReporteAgregado {
  n_usuarios_con_sesion_completada?: number;
  n_sesiones_completadas?: number;
  tasa_decisiones_seguras_global?: number;
  tasa_decisiones_seguras_por_rol?: Record<Rol, number>;
  n_reflexiones?: number;
  advertencia?: string;
  // forma "insuficiente"
  n_actual?: number;
  minimo_requerido?: number;
  mensaje?: string;
}
