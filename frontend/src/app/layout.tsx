import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MYCELIUM — Evolutionary Runtime",
  description: "Autonomous evolutionary software runtime - live genome visualization",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-mycelium-void text-mycelium-glow min-h-screen font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
