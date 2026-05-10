"use client";
import type { Acto } from "@/lib/types";
import { MensajeCorreo } from "./MensajeCorreo";
import { MensajeSMS } from "./MensajeSMS";
import { MensajeWhatsApp } from "./MensajeWhatsApp";

export function Dramatizacion({ acto }: { acto: Acto }) {
  if (acto.canal === "correo") return <MensajeCorreo acto={acto} />;
  if (acto.canal === "whatsapp") return <MensajeWhatsApp acto={acto} />;
  // sms / app_notificacion / llamada usan el render de SMS por simplicidad.
  return <MensajeSMS acto={acto} />;
}
