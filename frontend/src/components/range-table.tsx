import Link from "next/link";

import { formatNumber, formatPercent, formatPrice } from "@/lib/format";
import { RangeListItem } from "@/lib/types";

export function RangeTable({ rows }: { rows: RangeListItem[] }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Ticker</th>
              <th className="px-4 py-3">Range score</th>
              <th className="px-4 py-3">Opportunity</th>
              <th className="px-4 py-3">Close</th>
              <th className="px-4 py-3">Bounds</th>
              <th className="px-4 py-3">Containment</th>
              <th className="px-4 py-3">Touches</th>
              <th className="px-4 py-3">Setup</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row) => (
              <tr key={row.ticker} className="hover:bg-slate-50">
                <td className="px-4 py-4 align-top">
                  <Link href={`/stocks/${row.ticker}`} className="font-semibold text-slate-900 hover:text-teal-700">{row.ticker}</Link>
                  <p className="mt-1 max-w-xs text-xs text-slate-500">{row.name}</p>
                </td>
                <td className="px-4 py-4 font-semibold text-slate-900">{formatNumber(row.range_score, 1)}</td>
                <td className="px-4 py-4">{formatNumber(row.opportunity_score, 1)}</td>
                <td className="px-4 py-4">{formatPrice(row.latest_close)}</td>
                <td className="px-4 py-4 text-slate-600">{formatPrice(row.lower_bound)} / {formatPrice(row.upper_bound)}</td>
                <td className="px-4 py-4">{formatPercent(row.containment_ratio)}</td>
                <td className="px-4 py-4 text-slate-600">S {row.touch_counts.support} · R {row.touch_counts.resistance}</td>
                <td className="px-4 py-4">
                  {row.active_setup ? (
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${row.active_setup.direction === "long" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"}`}>
                      {row.active_setup.direction}
                    </span>
                  ) : (
                    <span className="text-slate-400">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
