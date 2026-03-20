import { AlertItem, OpportunityItem, PaginatedResponse, RangeDetail, RangeListItem } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { next: { revalidate: 60 } });
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getRanges(params = "?limit=25&sort_by=range_score&sort_order=desc") {
  return fetchJson<PaginatedResponse<RangeListItem>>(`/ranges${params}`);
}

export function getRangeDetail(ticker: string) {
  return fetchJson<RangeDetail>(`/ranges/${ticker}`);
}

export function getOpportunities() {
  return fetchJson<PaginatedResponse<OpportunityItem>>("/opportunities?page_size=5");
}

export function getAlerts() {
  return fetchJson<PaginatedResponse<AlertItem>>("/alerts?page_size=5");
}
