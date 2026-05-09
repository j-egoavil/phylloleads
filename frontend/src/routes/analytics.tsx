import { useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { Gauge, CheckSquare, Timer, TrendingUp } from "lucide-react";
import { useLeadStore } from "@/store/leadStore";
import { SOURCE_LABELS, type LeadSource } from "@/lib/mockData";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { formatPercent } from "@/lib/formatters";

export const Route = createFileRoute("/analytics")({
  head: () => ({ meta: [{ title: "Análisis · LeadFunnel" }] }),
  component: AnalyticsPage,
});

const PIE_COLORS = ["oklch(0.62 0.19 256)", "oklch(0.68 0.16 158)", "oklch(0.78 0.16 70)", "oklch(0.7 0.13 230)"];

function AnalyticsPage() {
  const leads = useLeadStore((s) => s.leads);

  const sourceData = useMemo(() => {
    const counts: Record<LeadSource, number> = { google_maps: 0, rues: 0, la_republica: 0 };
    leads.forEach((l) => { counts[l.source] += 1; });
    return (Object.keys(counts) as LeadSource[]).map((k) => ({ name: SOURCE_LABELS[k], value: counts[k] }));
  }, [leads]);

  const ruesByDay = useMemo(() => {
    const days: { day: string; validated: number; rejected: number }[] = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86400_000);
      const label = d.toLocaleDateString("es", { weekday: "short" });
      const dayLeads = leads.filter((l) => new Date(l.createdAt).toDateString() === d.toDateString());
      const validated = dayLeads.filter((l) => l.rues?.validated).length;
      const rejected = dayLeads.filter((l) => l.rues && !l.rues.validated).length;
      days.push({ day: label, validated, rejected });
    }
    return days;
  }, [leads]);

  const scoringTrend = useMemo(() => {
    const days: { day: string; A: number; B: number; C: number }[] = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86400_000);
      const label = d.toLocaleDateString("es", { weekday: "short" });
      const dayLeads = leads.filter((l) => new Date(l.createdAt).toDateString() === d.toDateString());
      days.push({
        day: label,
        A: dayLeads.filter((l) => l.category === "A").length,
        B: dayLeads.filter((l) => l.category === "B").length,
        C: dayLeads.filter((l) => l.category === "C").length,
      });
    }
    return days;
  }, [leads]);

  const kpis = useMemo(() => {
    const last24h = leads.filter((l) => Date.now() - new Date(l.createdAt).getTime() < 86400_000).length;
    const velocity = Math.round(last24h / 24);
    const validated = leads.filter((l) => l.rues?.validated).length;
    const validationRate = leads.length ? (validated / leads.length) * 100 : 0;
    const convertible = leads.filter((l) => l.category !== "C" && l.status !== "discarded").length;
    const discarded = leads.filter((l) => l.status === "discarded").length;
    return { velocity, validationRate, avgPhaseTime: 12.4, convertible, discarded };
  }, [leads]);

  return (
    <div className="space-y-6 max-w-[1400px] mx-auto">
      <div>
        <h2 className="text-2xl font-bold">Análisis del Embudo</h2>
        <p className="text-sm text-muted-foreground mt-1">KPIs en tiempo real del proceso de captación.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Velocity" value={kpis.velocity} icon={Gauge} tone="primary" suffix=" leads/h" />
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Validación RUES</div>
              <div className="mt-2 text-3xl font-bold tabular-nums">{formatPercent(kpis.validationRate)}</div>
              <div className="mt-1 text-xs text-success">▲ 3.2% vs semana anterior</div>
            </div>
            <div className="h-10 w-10 rounded-lg bg-success/10 text-success grid place-items-center"><CheckSquare className="h-5 w-5" /></div>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Tiempo prom. por fase</div>
              <div className="mt-2 text-3xl font-bold tabular-nums">{kpis.avgPhaseTime}<span className="text-base font-normal text-muted-foreground">s</span></div>
            </div>
            <div className="h-10 w-10 rounded-lg bg-warning/15 text-warning grid place-items-center"><Timer className="h-5 w-5" /></div>
          </div>
        </div>
        <MetricCard label="Convertibles" value={kpis.convertible} icon={TrendingUp} tone="success" suffix=" leads" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <h3 className="text-sm font-semibold mb-4">Distribución por fuente</h3>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sourceData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2}>
                  {sourceData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid oklch(0.92 0.01 255)" }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <h3 className="text-sm font-semibold mb-4">Validación RUES por día</h3>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ruesByDay} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.92 0.01 255)" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid oklch(0.92 0.01 255)" }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="validated" name="Validados" fill="oklch(0.68 0.16 158)" radius={[6, 6, 0, 0]} />
                <Bar dataKey="rejected" name="Rechazados" fill="oklch(0.62 0.23 25)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
        <h3 className="text-sm font-semibold mb-4">Progresión de scoring (A / B / C)</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={scoringTrend} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.92 0.01 255)" />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid oklch(0.92 0.01 255)" }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="A" stroke="oklch(0.68 0.16 158)" strokeWidth={2.5} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="B" stroke="oklch(0.78 0.16 70)" strokeWidth={2.5} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="C" stroke="oklch(0.5 0.03 257)" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
