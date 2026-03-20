import { AlertsSection } from "@/components/alerts-section";
import { DashboardShell } from "@/components/dashboard-shell";
import { OpportunitiesSection } from "@/components/opportunities-section";
import { RangeTable } from "@/components/range-table";
import { ScoreBadge } from "@/components/score-badge";
import { getAlerts, getOpportunities, getRanges } from "@/lib/api";

export default async function HomePage() {
  const [ranges, opportunities, alerts] = await Promise.all([getRanges(), getOpportunities(), getAlerts()]);
  const averageRangeScore = ranges.data.length
    ? ranges.data.reduce((sum, item) => sum + item.range_score, 0) / ranges.data.length
    : 0;
  const activeSetupCount = ranges.data.filter((item) => item.active_setup).length;

  return (
    <DashboardShell>
      <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-teal-700">MVP dashboard</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">Ranked range-bound stocks with explainable scores and setup levels.</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              The frontend consumes the FastAPI backend only. Use the screener table to inspect the highest-ranked candidates, then open a stock detail page for chart overlays and setup context.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            <ScoreBadge label="Qualified ranges" value={ranges.pagination.total_items} />
            <ScoreBadge label="Avg range score" value={averageRangeScore} />
            <ScoreBadge label="Active setups" value={activeSetupCount} />
          </div>
          <section className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Ranges table</h2>
              <p className="text-sm text-slate-500">Latest qualifying daily ranges sorted by composite score.</p>
            </div>
            <RangeTable rows={ranges.data} />
          </section>
        </div>
        <div className="space-y-6">
          <OpportunitiesSection opportunities={opportunities.data} />
          <AlertsSection alerts={alerts.data} />
        </div>
      </section>
    </DashboardShell>
  );
}
