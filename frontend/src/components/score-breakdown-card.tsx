import { formatNumber } from "@/lib/format";
import { RangeDetail } from "@/lib/types";

export function ScoreBreakdownCard({ detail }: { detail: RangeDetail }) {
  const entries = [
    ["Touch quality", detail.scores.components.touch_quality],
    ["Trend weakness", detail.scores.components.trend_weakness],
    ["Containment", detail.scores.components.containment_quality],
    ["Width vs ATR", detail.scores.components.range_width],
    ["Liquidity", detail.scores.components.liquidity],
    ["Opportunity location", detail.scores.components.current_opportunity_location],
  ] as const;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">Score breakdown</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {entries.map(([label, value]) => (
          <div key={label} className="rounded-xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">{formatNumber(value, 2)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
