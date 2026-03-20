import "./globals.css";

import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Range Trading Screener",
  description: "Dashboard for ranked range-bound stock setups.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-ink antialiased">{children}</body>
    </html>
  );
}
