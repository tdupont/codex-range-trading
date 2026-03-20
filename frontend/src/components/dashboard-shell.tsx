import Link from "next/link";
import { ReactNode } from "react";

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 text-ink">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-teal-700">Range Trading Screener</p>
            <h1 className="text-xl font-semibold text-slate-900">Daily S&amp;P 500 range setups</h1>
          </div>
          <nav className="flex gap-4 text-sm text-slate-600">
            <Link href="/" className="hover:text-slate-900">Dashboard</Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}
