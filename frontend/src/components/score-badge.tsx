import { formatNumber } from "@/lib/format";

export function ScoreBadge({ label, value }: { label: string; value: number | string }) {
  const numericValue = typeof value === "number" ? value : Number(value);
  const tone = numericValue >= 75 ? "bg-emerald-100 text-emerald-800" : numericValue >= 60 ? "bg-amber-100 text-amber-800" : "bg-slate-100 text-slate-700";
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-soft">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <div className={`mt-3 inline-flex rounded-full px-3 py-1 text-sm font-semibold ${tone}`}>{formatNumber(value, 1)}</div>
    </div>
  );
}
