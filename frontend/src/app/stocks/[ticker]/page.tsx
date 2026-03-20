import Link from "next/link";
import { notFound } from "next/navigation";

import { CandlestickRangeChart } from "@/components/candlestick-range-chart";
import { DashboardShell } from "@/components/dashboard-shell";
import { ScoreBadge } from "@/components/score-badge";
import { ScoreBreakdownCard } from "@/components/score-breakdown-card";
import { SetupCard } from "@/components/setup-card";
import { getRangeDetail } from "@/lib/api";
import { formatNumber, formatPercent, formatPrice } from "@/lib/format";

export default async function StockDetailPage({ params }: { params: { ticker: string } }) {
  try {
    const detail = await getRangeDetail(params.ticker.toUpperCase());
    return (
      <DashboardShell>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/" className="text-sm text-teal-700 hover:text-teal-800">← Back to dashboard</Link>
              <h2 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{detail.ticker} · {detail.name}</h2>
              <p className="mt-2 text-sm text-slate-500">As of {detail.as_of_date} · latest close {formatPrice(detail.latest_close)}</p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <ScoreBadge label="Range score" value={detail.scores.range_score} />
            <ScoreBadge label="Validity" value={detail.scores.range_validity_score} />
            <ScoreBadge label="Tradeability" value={detail.scores.tradeability_score} />
            <ScoreBadge label="Opportunity" value={detail.scores.opportunity_score} />
          </div>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
            <div className="mb-4 flex items-start justify-between gap-6">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">Chart</h3>
                <p className="text-sm text-slate-500">Candles, support/resistance zones, midline, current price, and setup levels.</p>
              </div>
              <div className="grid gap-2 text-xs text-slate-500 sm:grid-cols-2">
                <p>Support: {formatPrice(detail.range.support_zone.low)}–{formatPrice(detail.range.support_zone.high)}</p>
                <p>Resistance: {formatPrice(detail.range.resistance_zone.low)}–{formatPrice(detail.range.resistance_zone.high)}</p>
                <p>Midline: {formatPrice(detail.range.midline)}</p>
                <p>Containment: {formatPercent(detail.range.containment_ratio)}</p>
              </div>
            </div>
            <CandlestickRangeChart detail={detail} />
          </section>

          <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <div className="space-y-6">
              <ScoreBreakdownCard detail={detail} />
              <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
                <h2 className="text-lg font-semibold text-slate-900">Range diagnostics</h2>
                <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <Metric label="Upper bound" value={formatPrice(detail.range.upper_bound)} />
                  <Metric label="Lower bound" value={formatPrice(detail.range.lower_bound)} />
                  <Metric label="Width / ATR" value={formatNumber(detail.range.width_atr_multiple, 2)} />
                  <Metric label="ADX(14)" value={formatNumber(detail.indicators.adx_14, 2)} />
                  <Metric label="RSI(14)" value={formatNumber(detail.indicators.rsi_14, 2)} />
                  <Metric label="SMA20 slope" value={formatNumber(detail.indicators.sma_20_slope, 4)} />
                  <Metric label="Support touches" value={String(detail.range.touch_counts.support)} />
                  <Metric label="Resistance touches" value={String(detail.range.touch_counts.resistance)} />
                  <Metric label="Avg dollar vol" value={detail.indicators.avg_dollar_volume_20 ? formatPrice(detail.indicators.avg_dollar_volume_20) : "—"} />
                </div>
              </section>
            </div>
            <SetupCard setup={detail.setup} />
          </div>
        </div>
      </DashboardShell>
    );
  } catch {
    notFound();
  }
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-base font-semibold text-slate-900">{value}</p>
    </div>
  );
}
