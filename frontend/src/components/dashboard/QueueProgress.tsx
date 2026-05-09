import { Activity } from "lucide-react";
import { useLeadStore } from "@/store/leadStore";

export function QueueProgress() {
  const progress = useLeadStore((s) => s.queueProgress);
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold">Cola de procesamiento (Bull Queue)</span>
        </div>
        <span className="text-sm tabular-nums font-medium text-muted-foreground">{progress}%</span>
      </div>
      <div className="h-2.5 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary to-primary-glow transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="mt-2 text-xs text-muted-foreground">Procesando lotes de validación RUES y scoring…</div>
    </div>
  );
}
