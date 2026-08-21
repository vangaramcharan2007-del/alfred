import type { Metadata } from "next";
import "./globals.css";
import { JarvisProvider } from "@/context/JarvisContext";
import { HandshakeTransitionOverlay } from "@/components/hud/HandshakeTransitionOverlay";

export const metadata: Metadata = {
  title: "JARVIS X — Sovereign Persona-Adaptive HUD Engine",
  description: "Cybernetic Neural Lab & Wayne-Tech Tactical Intelligence HUD for Charan",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-persona="alfred">
      <body className="antialiased bg-background text-foreground min-h-screen relative overflow-x-hidden selection:bg-primary selection:text-black">
        <JarvisProvider>
          <HandshakeTransitionOverlay />
          {children}
        </JarvisProvider>
      </body>
    </html>
  );
}
