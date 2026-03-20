"use client";

import { useEffect, useRef } from "react";
import { ColorType, createChart } from "lightweight-charts";

import { RangeDetail } from "@/lib/types";

export function CandlestickRangeChart({ detail }: { detail: RangeDetail }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: { background: { type: ColorType.Solid, color: "#ffffff" }, textColor: "#0f172a" },
      grid: { vertLines: { color: "#e2e8f0" }, horzLines: { color: "#e2e8f0" } },
      rightPriceScale: { borderColor: "#cbd5e1" },
      timeScale: { borderColor: "#cbd5e1" },
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#0f766e",
      downColor: "#dc2626",
      borderVisible: false,
      wickUpColor: "#0f766e",
      wickDownColor: "#dc2626",
    });
    candleSeries.setData(
      detail.recent_candles.map((candle) => ({
        time: candle.date,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      })),
    );

    const overlay = (price: number, color: string) => {
      const line = chart.addLineSeries({ color, lineWidth: 2, priceLineVisible: false, lastValueVisible: false });
      line.setData(detail.recent_candles.map((candle) => ({ time: candle.date, value: price })));
      return line;
    };

    overlay(detail.range.support_zone.low, "#0f766e");
    overlay(detail.range.support_zone.high, "#14b8a6");
    overlay(detail.range.resistance_zone.low, "#f97316");
    overlay(detail.range.resistance_zone.high, "#dc2626");
    overlay(detail.range.midline, "#6366f1");
    overlay(detail.latest_close, "#0f172a");

    if (detail.setup) {
      overlay(detail.setup.stop_price, "#be123c");
      overlay(detail.setup.target_1, "#2563eb");
      overlay(detail.setup.target_2, "#1d4ed8");
    }

    chart.timeScale().fitContent();
    return () => chart.remove();
  }, [detail]);

  return <div ref={containerRef} className="h-[420px] w-full" />;
}
