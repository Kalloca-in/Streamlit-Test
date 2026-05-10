// Avatar ilustrativo (no fotorrealista). Genera iniciales sobre fondo
// con color derivado del nombre. Cumple el principio: "no usar fotos
// fotorrealistas de personas".
import { cn } from "@/lib/utils";

const PALETTE = ["#d97757", "#5b9aa0", "#b48d4a", "#8a6fbf", "#5fa86a", "#e3b15c"];

function colorFor(name: string) {
  let h = 0;
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return PALETTE[h % PALETTE.length];
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

export function Avatar({
  name,
  size = 56,
  className,
}: { name: string; size?: number; className?: string }) {
  const bg = colorFor(name);
  return (
    <div
      className={cn("rounded-full grid place-items-center font-serif font-medium select-none", className)}
      style={{ width: size, height: size, background: bg, color: "#0e0c0a" }}
      aria-hidden
    >
      {initials(name)}
    </div>
  );
}
