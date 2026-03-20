import { AlertItem } from "@/lib/types";

export function AlertsSection({ alerts }: { alerts: AlertItem[] }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-slate-900">Alerts</h2>
      <p className="mt-1 text-sm text-slate-500">Persisted setup alerts from the latest local scan.</p>
      <div className="mt-4 space-y-3">
        {alerts.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">Alerts placeholder: no stored alerts yet.</div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className="rounded-xl border border-slate-200 p-4">
              <div className="flex items-center justify-between gap-4">
                <p className="font-semibold text-slate-900">{alert.ticker}</p>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">{alert.direction ?? alert.alert_type}</span>
              </div>
              <p className="mt-2 text-sm text-slate-600">{alert.message}</p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
