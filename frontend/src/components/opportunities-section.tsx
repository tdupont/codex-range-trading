import Link from "next/link";

import { formatNumber, formatPrice } from "@/lib/format";
import { OpportunityItem } from "@/lib/types";

export function OpportunitiesSection({ opportunities }: { opportunities: OpportunityItem[] }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Top opportunities</h2>
          <p className="text-sm text-slate-500">Only active long and short setups from the latest scan.</p>
        </div>
      </div>
      <div className="space-y-3">
        {opportunities.length === 0 ? (
          <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">No active setups are available yet.</p>
        ) : (
          opportunities.map((item) => (
            <Link key={`${item.ticker}-${item.direction}`} href={`/stocks/${item.ticker}`} className="flex items-center justify-between rounded-xl border border-slate-200 p-4 hover:border-slate-300 hover:bg-slate-50">
              <div>
                <p className="font-semibold text-slate-900">{item.ticker}</p>
                <p className="text-sm text-slate-500">{item.direction.toUpperCase()} · score {formatNumber(item.opportunity_score, 1)}</p>
              </div>
              <div className="text-right text-sm text-slate-600">
                <p>Entry {formatPrice(item.entry_zone_low)}–{formatPrice(item.entry_zone_high)}</p>
                <p>Stop {formatPrice(item.stop_price)}</p>
              </div>
            </Link>
          ))
        )}
      </div>
    </section>
  );
}
