export type PriceZone = {
  low: number;
  high: number;
};

export type TouchCounts = {
  support: number;
  resistance: number;
};

export type SetupSummary = {
  direction: "long" | "short";
  status: string;
  entry_zone_low: number;
  entry_zone_high: number;
  stop_price: number;
  target_1: number;
  target_2: number;
  rejection_signal?: string | null;
};

export type RangeListItem = {
  ticker: string;
  name: string;
  as_of_date: string;
  range_score: number;
  range_validity_score: number;
  tradeability_score: number;
  opportunity_score: number;
  upper_bound: number;
  lower_bound: number;
  midline: number;
  support_zone: PriceZone;
  resistance_zone: PriceZone;
  touch_counts: TouchCounts;
  containment_ratio: number;
  atr_14: number | null;
  adx_14: number | null;
  latest_close: number;
  active_setup: SetupSummary | null;
};

export type RangeDetail = {
  ticker: string;
  name: string;
  as_of_date: string;
  latest_close: number;
  range: {
    qualified: boolean;
    lookback_days: number;
    upper_bound: number;
    lower_bound: number;
    midline: number;
    width: number;
    width_atr_multiple: number;
    support_zone: PriceZone;
    resistance_zone: PriceZone;
    touch_counts: TouchCounts;
    containment_ratio: number;
  };
  indicators: {
    adx_14: number | null;
    atr_14: number | null;
    rsi_14: number | null;
    sma_20: number | null;
    sma_20_slope: number | null;
    avg_dollar_volume_20?: number | null;
  };
  scores: {
    range_score: number;
    range_validity_score: number;
    tradeability_score: number;
    opportunity_score: number;
    components: {
      touch_quality: number;
      trend_weakness: number;
      containment_quality: number;
      range_width: number;
      liquidity: number;
      current_opportunity_location: number;
    };
  };
  setup: SetupSummary | null;
  recent_candles: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
};

export type OpportunityItem = {
  ticker: string;
  as_of_date: string;
  direction: "long" | "short";
  opportunity_score: number;
  latest_close: number;
  entry_zone_low: number;
  entry_zone_high: number;
  stop_price: number;
  target_1: number;
  target_2: number;
};

export type AlertItem = {
  id: number;
  ticker: string;
  created_at: string;
  alert_type: string;
  direction: "long" | "short" | null;
  message: string;
  related_range_score: number | null;
};

export type PaginatedResponse<T> = {
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
};
