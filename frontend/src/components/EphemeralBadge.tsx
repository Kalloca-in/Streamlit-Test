"use client";
import { ShieldOff } from "lucide-react";

export function EphemeralBadge({ remaining }: { remaining?: number }) {
  return (
    <div className="badge-ephemeral">
      <ShieldOff size={12} />
      <span>Sesión efímera — al cerrar, se borra todo</span>
      {typeof remaining === "number" && (
        <span className="ml-1 opacity-70">· {Math.floor(remaining / 60)}m restantes</span>
      )}
    </div>
  );
}
