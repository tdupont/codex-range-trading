import { formatPrice } from "@/lib/format";
import { SetupSummary } from "@/lib/types";

export function SetupCard({ setup }: { setup: SetupSummary | null }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">Trade setup</h2>
      {!setup ? (
        <p className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">No active setup is available for the latest range snapshot.</p>
      ) : (
        <div className="mt-4 space-y-3 text-sm text-slate-600">
          <p><span className="font-semibold text-slate-900">Direction:</span> {setup.direction.toUpperCase()}</p>
          <p><span className="font-semibold text-slate-900">Entry zone:</span> {formatPrice(setup.entry_zone_low)}–{formatPrice(setup.entry_zone_high)}</p>
          <p><span className="font-semibold text-slate-900">Stop:</span> {formatPrice(setup.stop_price)}</p>
          <p><span className="font-semibold text-slate-900">Target 1:</span> {formatPrice(setup.target_1)}</p>
          <p><span className="font-semibold text-slate-900">Target 2:</span> {formatPrice(setup.target_2)}</p>
          <p><span className="font-semibold text-slate-900">Signal:</span> {setup.rejection_signal ?? "None"}</p>
        </div>
      )}
    </section>
  );
}
