import type { Rol } from "@/lib/types";
import { rolLabel } from "@/lib/utils";

export function RolPill({ rol }: { rol: Rol }) {
  return (
    <span className={`role-pill role-pill--${rol}`}>
      <span className="w-2 h-2 rounded-full bg-current" />
      {rolLabel[rol]}
    </span>
  );
}
