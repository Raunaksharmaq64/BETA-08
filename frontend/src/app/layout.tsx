import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

export const metadata: Metadata = {
  title: "RIGHT FIT — Career Intelligence Platform",
  description: "AI-Powered Career Intelligence, Resume Verification, and Governed Job Sourcing Platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="h-full">
      <body suppressHydrationWarning className="min-h-full flex flex-col font-sans antialiased text-[#171c23]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
