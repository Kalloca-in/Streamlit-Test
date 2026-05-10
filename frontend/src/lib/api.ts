const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
export const WS_BASE = process.env.NEXT_PUBLIC_WS_BASE || "ws://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) }
  });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`API ${r.status} ${path}: ${text || r.statusText}`);
  }
  return r.json() as Promise<T>;
}

export type AttackerCard = {
  code: string;
  display_name: string;
  short_description: string;
  techniques: string[];
  sample_opening: string;
  psychological_profile: string;
  accent_color: string;
};

export type CharacterCard = {
  code: string;
  display_name: string;
  age?: number | null;
  role_title: string;
  fictional_company?: string | null;
  fictional_family_context?: string | null;
  exposure_profile: string;
  archetype_marco?: string | null;
  hierarchy_level?: string | null;
};

export type Catalogs = {
  archetypes: AttackerCard[];
  universal_characters: CharacterCard[];
  organizational_controls: { code: string; display_name: string; description: string; when_to_apply: string; example_invocation: string; expected_outcome: string }[];
};

export type SessionConfigPayload = {
  level: number;
  archetype?: string;
  defender_kind: "self" | "universal_character" | "corporate_character";
  universal_character_code?: string | null;
};

export type SessionCreated = {
  session_id: string;
  level: number;
  special_mode: "none" | "demostracion" | "caja_negra";
  ttl_seconds: number;
  archetype: string | null;
  objective: string;
  defender: { kind: string; character?: CharacterCard | null };
};

export type DebriefBundle = {
  summary: { status: string; turns: number; duration_seconds: number; headline: string };
  confession: string;
  annotations: { turn_index: number; label: string; note: string }[];
  can_replay: boolean;
  mirror_prompt: string | null;
  deletion_manifest: string[];
};

export type DemoBundle = {
  title: string;
  description: string;
  character_code: string;
  archetype: string;
  objective: string;
  script: { role: "attacker" | "defender"; content: string; annotation: string }[];
  closing: {
    headline: string;
    controls_that_would_have_stopped_it: { code: string; lesson: string; display_name?: string; description?: string }[];
  };
};

export const api = {
  catalogs: () => request<Catalogs>("/sessions/catalogs"),
  createSession: (cfg: SessionConfigPayload) =>
    request<SessionCreated>("/sessions", { method: "POST", body: JSON.stringify(cfg) }),
  getSession: (id: string) => request<any>(`/sessions/${id}`),
  endSession: (id: string) => request<{ removed_keys: string[] }>(`/sessions/${id}`, { method: "DELETE" }),
  debrief: (id: string) => request<DebriefBundle>(`/debrief/${id}`),
  wipe: (id: string) => request<{ removed_keys: string[]; ok: boolean }>(`/debrief/${id}/wipe`, { method: "POST" }),
  demoLevel11: () => request<DemoBundle>("/demo/nivel-11")
};
