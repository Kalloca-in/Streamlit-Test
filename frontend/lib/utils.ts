import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const arquetipoLabel: Record<string, string> = {
  guardian_financiero: "Guardián Financiero",
  arquitecto_digital: "Arquitecto Digital",
  rostro_experiencias: "Rostro de Experiencias",
  cuidador_familiar: "Cuidador Familiar",
  ejecutivo_transito: "Ejecutivo en Tránsito",
  operador_confianza: "Operador de Confianza",
};

export const ganchoLabel: Record<string, string> = {
  urgencia: "Urgencia",
  autoridad: "Autoridad",
  miedo: "Miedo",
  curiosidad: "Curiosidad",
  reciprocidad: "Reciprocidad",
  escasez: "Escasez",
  prueba_social: "Prueba social",
  afecto: "Afecto",
};

export const rolLabel: Record<string, string> = {
  ciudadano: "Ciudadano",
  colaborador: "Colaborador",
  cliente: "Cliente",
};

export const canalLabel: Record<string, string> = {
  sms: "SMS",
  whatsapp: "Mensajería",
  correo: "Correo",
  llamada: "Llamada",
  app_notificacion: "Notificación",
};

export const tipoIndicadorLabel: Record<string, string> = {
  dominio_sospechoso: "Dominio sospechoso",
  urgencia_artificial: "Urgencia artificial",
  llamado_accion_unico: "Llamado a acción único",
  autoridad_no_verificable: "Autoridad no verificable",
  incongruencia_canal: "Incongruencia de canal",
  error_contexto: "Error de contexto",
  error_ortografia: "Error de ortografía",
  remitente_anomalo: "Remitente anómalo",
  solicitud_datos_sensibles: "Solicitud de datos sensibles",
  amenaza_velada: "Amenaza velada",
  oferta_desproporcionada: "Oferta desproporcionada",
  enlace_acortado: "Enlace acortado",
};

export const horaPorRol: Record<string, string> = {
  ciudadano: "07:30 — Mañana",
  colaborador: "11:00 — Mediodía",
  cliente: "19:00 — Tarde / noche",
};
