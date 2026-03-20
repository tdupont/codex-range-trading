import Link from "next/link";

import { DashboardShell } from "@/components/dashboard-shell";

export default function NotFound() {
  return (
    <DashboardShell>
      <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-soft">
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Not found</p>
        <h2 className="mt-3 text-2xl font-semibold text-slate-900">We couldn&apos;t find that ticker snapshot.</h2>
        <p className="mt-3 text-sm text-slate-600">Try another symbol from the ranked dashboard results.</p>
        <Link href="/" className="mt-6 inline-flex rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-700">
          Back to dashboard
        </Link>
      </div>
    </DashboardShell>
  );
}
