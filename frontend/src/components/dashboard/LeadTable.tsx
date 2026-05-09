import { useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowUpDown, ChevronRight } from "lucide-react";
import { useLeadStore } from "@/store/leadStore";
import { SOURCE_LABELS, STATUS_LABELS, type Lead, type LeadStatus } from "@/lib/mockData";
import { formatAbsolute, formatRelative } from "@/lib/formatters";

const statusTone: Record<LeadStatus, string> = {
  search: "bg-muted text-muted-foreground",
  captured: "bg-info/15 text-info",
  validating: "bg-warning/15 text-warning",
  scored: "bg-primary/15 text-primary",
  contacted: "bg-success/15 text-success",
  discarded: "bg-muted text-muted-foreground line-through",
  error: "bg-destructive/15 text-destructive",
};

type SortKey = "name" | "company" | "source" | "status" | "score" | "createdAt";

export function LeadTable({ limit }: { limit?: number }) {
  const leads = useLeadStore((s) => s.leads);
  const filters = useLeadStore((s) => s.filters);
  const niches = useLeadStore((s) => s.niches);
  const nicheLabels = useLeadStore((s) => s.nicheLabels);
  const [sortKey, setSortKey] = useState<SortKey>("createdAt");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const filtered = useMemo(() => {
    const q = filters.search.toLowerCase().trim();
    let arr = leads.filter((l) => {
      if (filters.status !== "all" && l.status !== filters.status) return false;
      if (filters.source !== "all" && l.source !== filters.source) return false;
      if (filters.category !== "all" && l.category !== filters.category) return false;
      if (!niches[l.niche]) return false;
      if (q && !`${l.name} ${l.company} ${l.email}`.toLowerCase().includes(q)) return false;
      return true;
    });
    arr = [...arr].sort((a, b) => {
      const av = a[sortKey] as string | number;
      const bv = b[sortKey] as string | number;
      const cmp = av > bv ? 1 : av < bv ? -1 : 0;
      return sortDir === "asc" ? cmp : -cmp;
    });
    return limit ? arr.slice(0, limit) : arr;
  }, [leads, filters, niches, sortKey, sortDir, limit]);

  const toggleSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir("desc"); }
  };

  const Th = ({ k, children }: { k: SortKey; children: React.ReactNode }) => (
    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      <button onClick={() => toggleSort(k)} className="flex items-center gap-1 hover:text-foreground">
        {children} <ArrowUpDown className="h-3 w-3 opacity-50" />
      </button>
    </th>
  );

  if (!filtered.length) {
    return (
      <div className="rounded-xl border border-dashed border-border bg-card p-12 text-center text-sm text-muted-foreground">
        No hay leads que coincidan con los filtros.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/40 border-b border-border">
            <tr>
              <Th k="name">Contacto</Th>
              <Th k="company">Empresa</Th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Nicho</th>
              <Th k="source">Fuente</Th>
              <Th k="status">Estado</Th>
              <Th k="score">Score</Th>
              <Th k="createdAt">Creado</Th>
              <th />
            </tr>
          </thead>
          <tbody>
            {filtered.map((l: Lead) => (
              <tr key={l.id} className="border-b border-border last:border-0 hover:bg-accent/40 transition-colors">
                <td className="px-4 py-3">
                  <div className="font-medium text-foreground">{l.name}</div>
                  <div className="text-xs text-muted-foreground">{l.email}</div>
                </td>
                <td className="px-4 py-3 text-foreground">{l.company}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center rounded-full bg-accent text-accent-foreground px-2 py-0.5 text-xs">
                    {nicheLabels[l.niche] ?? l.niche}
                  </span>
                </td>
                <td className="px-4 py-3 text-muted-foreground">{SOURCE_LABELS[l.source]}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusTone[l.status]}`}>
                    {STATUS_LABELS[l.status]}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className={`tabular-nums font-semibold w-8 ${l.category === "A" ? "text-success" : l.category === "B" ? "text-warning" : "text-destructive"}`}>{l.score}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${l.category === "A" ? "bg-success/15 text-success" : l.category === "B" ? "bg-warning/15 text-warning" : "bg-destructive/15 text-destructive"}`}>
                      {l.category}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-muted-foreground tabular-nums" title={formatRelative(l.createdAt)}>
                  {formatAbsolute(l.createdAt)}
                </td>
                <td className="px-4 py-3">
                  <Link to="/leads/$id" params={{ id: l.id }} className="inline-flex items-center text-primary hover:text-primary-glow text-xs font-medium">
                    Ver <ChevronRight className="h-3 w-3" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
