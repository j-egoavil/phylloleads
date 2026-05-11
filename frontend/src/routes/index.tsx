import { useEffect, useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Users, CheckCircle2, Loader2, AlertTriangle, Search } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { QueueProgress } from "@/components/dashboard/QueueProgress";
import { LeadTable } from "@/components/dashboard/LeadTable";
import { useLeadStore } from "@/store/leadStore";
import { SOURCE_LABELS, STATUS_LABELS, type LeadSource, type LeadStatus } from "@/lib/mockData";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [{ title: "Dashboard · LeadFunnel" }] }),
  component: Dashboard,
});

function useDebounced<T>(v: T, ms = 300) {
  const [d, setD] = useState(v);
  useEffect(() => { const t = setTimeout(() => setD(v), ms); return () => clearTimeout(t); }, [v, ms]);
  return d;
}

function Dashboard() {
  const leads = useLeadStore((s) => s.leads);
  const filters = useLeadStore((s) => s.filters);
  const setFilter = useLeadStore((s) => s.setFilter);
  const addLeads = useLeadStore((s) => s.addLeads);

  const [searchInput, setSearchInput] = useState(filters.search);
  const debouncedSearch = useDebounced(searchInput, 300);

  useEffect(() => { setFilter("search", debouncedSearch); }, [debouncedSearch, setFilter]);

  const metrics = useMemo(() => {
    const total = leads.length;
    const validated = leads.filter((l) => l.rues?.validated).length;
    const inProcess = leads.filter((l) => ["search", "captured", "validating"].includes(l.status)).length;
    const errors = leads.filter((l) => l.status === "error").length;
    return { total, validated, inProcess, errors };
  }, [leads]);

  const hourlyData = useMemo(() => {
    const buckets: Record<number, number> = {};
    const now = Date.now();
    for (let i = 23; i >= 0; i--) buckets[i] = 0;
    leads.forEach((l) => {
      const h = Math.floor((now - new Date(l.createdAt).getTime()) / 3600_000);
      if (h >= 0 && h <= 23) buckets[h] += 1;
    });
    return Array.from({ length: 24 }, (_, i) => ({ hour: `${23 - i}h`, leads: buckets[23 - i] }));
  }, [leads]);

  return (
    <div className="space-y-6 max-w-[1400px] mx-auto">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Total Leads" value={metrics.total} icon={Users} delta={8.2} tone="primary" />
        <MetricCard label="Validados RUES" value={metrics.validated} icon={CheckCircle2} delta={4.1} tone="success" />
        <MetricCard label="En Proceso" value={metrics.inProcess} icon={Loader2} delta={-2.3} tone="warning" />
        <MetricCard label="Errores" value={metrics.errors} icon={AlertTriangle} delta={-1.4} tone="destructive" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold">Leads ingresados (últimas 24h)</h2>
              <p className="text-xs text-muted-foreground">Actualizado en tiempo real vía Socket.io</p>
            </div>
          </div>
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourlyData} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <defs>
                  <linearGradient id="lg" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="oklch(0.62 0.19 256)" />
                    <stop offset="100%" stopColor="oklch(0.72 0.17 250)" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.92 0.01 255)" />
                <XAxis dataKey="hour" tick={{ fontSize: 11 }} stroke="oklch(0.5 0.03 257)" />
                <YAxis tick={{ fontSize: 11 }} stroke="oklch(0.5 0.03 257)" />
                <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid oklch(0.92 0.01 255)" }} />
                <Line type="monotone" dataKey="leads" stroke="url(#lg)" strokeWidth={3} dot={false} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <QueueProgress />
      </div>

      <div className="rounded-xl border border-border bg-card p-5 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-semibold">Leads recientes</h2>
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input
                placeholder="Buscar empresa, contacto…"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="h-9 pl-8 pr-3 rounded-md border border-input bg-background text-sm w-56 focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <select
              value={filters.source}
              onChange={(e) => setFilter("source", e.target.value as LeadSource | "all")}
              className="h-9 px-2 rounded-md border border-input bg-background text-sm"
            >
              <option value="all">Todas las fuentes</option>
              {Object.entries(SOURCE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select
              value={filters.status}
              onChange={(e) => setFilter("status", e.target.value as LeadStatus | "all")}
              className="h-9 px-2 rounded-md border border-input bg-background text-sm"
            >
              <option value="all">Todos los estados</option>
              {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <select
              value={filters.category}
              onChange={(e) => setFilter("category", e.target.value as "A" | "B" | "C" | "all")}
              className="h-9 px-2 rounded-md border border-input bg-background text-sm"
            >
              <option value="all">Todas las categorías</option>
              <option value="A">A — Alto</option>
              <option value="B">B — Medio</option>
              <option value="C">C — Bajo</option>
            </select>
          </div>
        </div>
        <LeadTable limit={15} />
      </div>

    </div>
  );
}
