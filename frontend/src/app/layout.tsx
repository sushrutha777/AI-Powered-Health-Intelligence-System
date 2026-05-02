import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: "Health Intelligence System — AI-Powered Healthcare Platform",
  description:
    "Advanced AI healthcare platform providing disease prediction, heart disease risk assessment, drug recommendations, and an intelligent medical chatbot.",
  keywords: ["healthcare", "AI", "disease prediction", "medical chatbot", "drug recommendation"],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
