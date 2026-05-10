import "./globals.css";
import type { Metadata } from "next";
import { DisclaimerBar } from "@/components/DisclaimerBar";

export const metadata: Metadata = {
  title: "CiberTeatro — Awareness dramatizada en triple rol",
  description:
    "Aprende a reconocer ataques de spearphishing observando cómo se construyen, no padeciéndolos.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen">
        <DisclaimerBar />
        <main className="min-h-[calc(100vh-2rem)]">{children}</main>
        <footer className="mt-16 border-t border-white/5 py-8 text-center text-xs text-muted">
          CiberTeatro · Plataforma de awareness dramatizada · Contenido ficticio.
        </footer>
      </body>
    </html>
  );
}
