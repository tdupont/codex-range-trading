function normalizeNumber(value: number | string | null | undefined) {
  if (value === null || value === undefined) return null;
  const numeric = typeof value === "number" ? value : Number(value);
  return Number.isNaN(numeric) ? null : numeric;
}

export function formatPrice(value: number | string | null | undefined) {
  const numeric = normalizeNumber(value);
  if (numeric === null) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(numeric);
}

export function formatNumber(value: number | string | null | undefined, digits = 2) {
  const numeric = normalizeNumber(value);
  if (numeric === null) return "—";
  return numeric.toFixed(digits);
}

export function formatPercent(value: number | string | null | undefined) {
  const numeric = normalizeNumber(value);
  if (numeric === null) return "—";
  return `${(numeric * 100).toFixed(1)}%`;
}
