// Persistencia mínima en localStorage del usuario anónimo de la app.
// La plataforma NO recolecta OSINT del usuario real; solo guarda
// identificadores opacos por sesión para retomar el progreso.

const KEY_USUARIO = "ciberteatro:usuario_id";
const KEY_ORG = "ciberteatro:organizacion_id";
const KEY_SESION_ACTUAL = "ciberteatro:sesion_actual";

export const sesionLocal = {
  getUsuarioId(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(KEY_USUARIO);
  },
  setUsuarioId(id: string) {
    window.localStorage.setItem(KEY_USUARIO, id);
  },
  getOrganizacionId(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(KEY_ORG);
  },
  setOrganizacionId(id: string) {
    window.localStorage.setItem(KEY_ORG, id);
  },
  getSesionActual(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(KEY_SESION_ACTUAL);
  },
  setSesionActual(id: string) {
    window.localStorage.setItem(KEY_SESION_ACTUAL, id);
  },
  clearSesionActual() {
    window.localStorage.removeItem(KEY_SESION_ACTUAL);
  },
};
