// Cliente HTTP simple. Usa el rewrite de Next a /api → backend.
import type {
  Acto, Arquetipo, DiaTriple, Decision, MarcaFicticia, Personaje,
  ProgresoUsuario, ReporteAgregado, Rol, Sesion,
} from "./types";

const BASE = "/api";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    ...init,
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`API ${r.status}: ${text}`);
  }
  return r.json() as Promise<T>;
}

export const api = {
  marcas: () => http<MarcaFicticia[]>("/marcas"),

  listarPersonajes: (params?: { arquetipo?: Arquetipo; nivel?: number; soloSemilla?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.arquetipo) q.set("arquetipo", params.arquetipo);
    if (params?.nivel) q.set("nivel", String(params.nivel));
    if (params?.soloSemilla) q.set("solo_semilla", "true");
    const qs = q.toString() ? `?${q}` : "";
    return http<Personaje[]>(`/personajes${qs}`);
  },
  obtenerPersonaje: (id: string) => http<Personaje>(`/personajes/${id}`),

  listarDiasTriplesPorPersonaje: (personajeId: string) =>
    http<DiaTriple[]>(`/dias-triples/personaje/${personajeId}`),
  obtenerDiaTriple: (id: string) => http<DiaTriple>(`/dias-triples/${id}`),

  crearOrganizacion: (body: { nombre: string; slug: string; sector?: string }) =>
    http<{ id: string }>("/organizaciones", { method: "POST", body: JSON.stringify(body) }),
  crearUsuarioAnonimo: (organizacion_id: string, identificador_externo: string) =>
    http<{ id: string }>("/usuarios", {
      method: "POST",
      body: JSON.stringify({ organizacion_id, identificador_externo }),
    }),

  crearSesion: (b: { usuario_id: string; personaje_id: string; dia_triple_id: string }) =>
    http<Sesion>("/sesiones", { method: "POST", body: JSON.stringify(b) }),
  obtenerSesion: (id: string) => http<Sesion>(`/sesiones/${id}`),
  registrarDecision: (sesionId: string, body: {
    acto_id: string; rol: Rol; opcion_elegida: string; indicadores_detectados: string[];
  }) =>
    http<Decision>(`/sesiones/${sesionId}/decisiones`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  registrarReflexion: (sesionId: string, body: {
    rol_mas_vulnerable?: Rol | null; eco_personal?: string | null;
    cambio_propuesto?: string | null; nivel_confianza?: number | null;
  }) =>
    http(`/sesiones/${sesionId}/reflexion`, { method: "POST", body: JSON.stringify(body) }),
  progresoUsuario: (uid: string) =>
    http<ProgresoUsuario>(`/sesiones/usuario/${uid}/progreso`),

  diseccionActo: (actoId: string) => http(`/disecciones/acto/${actoId}`),

  reporteAgregado: (orgId: string) =>
    http<ReporteAgregado>(`/reportes/organizacion/${orgId}/agregado`),
};
