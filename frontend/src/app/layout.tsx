import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CiberSpar — sparring contra ingeniería social",
  description:
    "Entrena tu defensa conversacional contra ingeniería social en sesiones efímeras y adaptativas."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-paper text-ink antialiased">{children}</body>
    </html>
  );
}
