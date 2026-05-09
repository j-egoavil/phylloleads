import type { LucideIcon } from "lucide-react";
import { formatNumber } from "@/lib/formatters";

interface Props {
  label: string;
  value: number;
  delta?: number;
  icon: LucideIcon;
  tone?: "primary" | "success" | "warning" | "destructive";
  suffix?: string;
}

const toneClasses: Record<NonNullable<Props["tone"]>, string> = {
  primary: "bg-primary/10 text-primary",
  success: "bg-success/10 text-success",
  warning: "bg-warning/15 text-warning",
  destructive: "bg-destructive/10 text-destructive",
};

export function MetricCard({ label, value, delta, icon: Icon, tone = "primary", suffix }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{label}</div>
          <div className="mt-2 text-3xl font-bold tabular-nums">
            {formatNumber(value)}
            {suffix && <span className="text-base font-normal text-muted-foreground">{suffix}</span>}
          </div>
          {delta !== undefined && (
            <div className={`mt-1 text-xs font-medium ${delta >= 0 ? "text-success" : "text-destructive"}`}>
              {delta >= 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}% vs ayer
            </div>
          )}
        </div>
        <div className={`h-10 w-10 rounded-lg grid place-items-center ${toneClasses[tone]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
