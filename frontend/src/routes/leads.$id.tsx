import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { ArrowLeft, Building2, Phone, Mail, MapPin, FileCheck2, XCircle, Sparkles, CheckCircle2, MinusCircle } from "lucide-react";
import { toast } from "sonner";
import { useLeadStore } from "@/store/leadStore";
import { SOURCE_LABELS, STATUS_LABELS } from "@/lib/mockData";
import { formatAbsolute, formatRelative } from "@/lib/formatters";

export const Route = createFileRoute("/leads/$id")({
  head: ({ params }) => ({ meta: [{ title: `Lead ${params.id} · LeadFunnel` }] }),
  component: LeadDetail,
  notFoundComponent: () => (
    <div className="text-center py-20">
      <h2 className="text-xl font-semibold">Lead no encontrado</h2>
      <Link to="/" className="text-primary text-sm mt-3 inline-block">← Volver al dashboard</Link>
    </div>
  ),
});

function LeadDetail() {
  const { id } = Route.useParams();
  const navigate = useNavigate();
  const lead = useLeadStore((s) => s.leads.find((l) => l.id === id));
  const updateLead = useLeadStore((s) => s.updateLead);

  if (!lead) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-semibold">Lead no encontrado</h2>
        <Link to="/" className="text-primary text-sm mt-3 inline-block">← Volver al dashboard</Link>
      </div>
    );
  }

  const handleContact = () => {
    updateLead(lead.id, { status: "contacted" });
    toast.success("Lead marcado como contactado");
  };
  const handleDiscard = () => {
    updateLead(lead.id, { status: "discarded" });
    toast.info("Lead descartado");
    navigate({ to: "/" });
  };
  const handleEnrich = () => {
    const newScore = Math.min(100, lead.score + Math.floor(Math.random() * 12) + 3);
    updateLead(lead.id, { score: newScore, category: newScore >= 75 ? "A" : newScore >= 50 ? "B" : "C" });
    toast.success("Lead enriquecido", { description: `Nuevo score: ${newScore}` });
  };
  const handleReduce = () => {
    const newScore = Math.max(0, lead.score - (Math.floor(Math.random() * 12) + 3));
    updateLead(lead.id, { score: newScore, category: newScore >= 75 ? "A" : newScore >= 50 ? "B" : "C" });
    toast.info("Score reducido", { description: `Nuevo score: ${newScore}` });
  };

  const categoryGradient =
    lead.category === "A" ? "from-success to-success/70"
    : lead.category === "B" ? "from-warning to-warning/70"
    : "from-destructive to-destructive/70";

  return (
    <div className="space-y-6 max-w-[1200px] mx-auto">
      <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Volver
      </Link>

      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">{lead.niche || 'General'}</div>
            <h1 className="text-3xl font-bold mt-1">{lead.name || 'Sin nombre'}</h1>
            <p className="text-muted-foreground mt-1">{lead.city || 'Ciudad desconocida'}</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleEnrich} className="inline-flex items-center gap-1.5 rounded-lg border border-input bg-background hover:bg-accent px-3 py-2 text-sm font-medium">
              <Sparkles className="h-4 w-4" /> Enriquecer
            </button>
            <button onClick={handleReduce} className="inline-flex items-center gap-1.5 rounded-lg border border-input bg-background hover:bg-accent px-3 py-2 text-sm font-medium">
              <MinusCircle className="h-4 w-4" /> Reducir score
            </button>
            <button onClick={handleDiscard} className="inline-flex items-center gap-1.5 rounded-lg border border-destructive/30 text-destructive hover:bg-destructive/10 px-3 py-2 text-sm font-medium">
              <XCircle className="h-4 w-4" /> Descartar
            </button>
            <button onClick={handleContact} className="inline-flex items-center gap-1.5 rounded-lg bg-success text-success-foreground hover:opacity-90 px-3 py-2 text-sm font-medium">
              <CheckCircle2 className="h-4 w-4" /> Marcar contactado
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
            <h3 className="text-sm font-semibold mb-4">Información de contacto</h3>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <Field icon={Building2} label="Nicho" value={lead.niche} />
              <Field icon={Phone} label="Teléfono" value={lead.phone} />
              <Field icon={Mail} label="Website" value={lead.website} />
              <Field icon={MapPin} label="Dirección" value={lead.address} />
            </dl>
          </div>

          {/* Sección de historial omitida - no disponible en API */}
          {/* Sección de validación RUES omitida - no disponible en API */}
        </div>

        <div className="space-y-4">
          <div className={`rounded-xl border border-border bg-gradient-to-br ${categoryGradient} text-white p-6 shadow-md`}>
            <div className="text-xs uppercase tracking-wider opacity-80">Lead Score</div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-6xl font-bold tabular-nums">{lead.score}</span>
              <span className="opacity-80">/100</span>
            </div>
            <div className="mt-4 h-2 rounded-full bg-white/20 overflow-hidden">
              <div className="h-full bg-white transition-all" style={{ width: `${lead.score}%` }} />
            </div>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs uppercase tracking-wider opacity-80">Categoría</span>
              <span className="px-3 py-1 rounded-full bg-white/20 backdrop-blur text-lg font-bold">{lead.category}</span>
            </div>
            <div className="mt-2 text-xs opacity-80">
              {lead.category === "A" && "Alto potencial — priorizar contacto"}
              {lead.category === "B" && "Medio potencial — nutrir"}
              {lead.category === "C" && "Bajo potencial — descartar o reciclar"}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
            <h3 className="text-sm font-semibold mb-3">Estado actual</h3>
            <div className="text-2xl font-bold">{STATUS_LABELS[lead.status]}</div>
            <div className="text-xs text-muted-foreground mt-1" title={formatRelative(lead.createdAt)}>Creado {formatAbsolute(lead.createdAt)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({ icon: Icon, label, value }: { icon: typeof Building2; label: string; value?: string }) {
  const missing = !value;
  return (
    <div className="flex items-start gap-3">
      <div className="h-8 w-8 rounded-md bg-muted grid place-items-center text-muted-foreground"><Icon className="h-4 w-4" /></div>
      <div className="min-w-0">
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className={`font-medium truncate ${missing ? "text-destructive" : ""}`}>{missing ? "N/A" : value}</div>
      </div>
    </div>
  );
}
