import { useEffect, useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Play, Pause, MapPin, FileCheck2, Newspaper, Clock, Filter, Utensils, Cpu, HeartPulse, ShoppingBag, Wrench, HardHat, GraduationCap, Landmark, Sparkles, Loader2, X } from "lucide-react";
import { toast } from "sonner";
import { useLeadStore } from "@/store/leadStore";
import { SOURCE_LABELS, type LeadSource, type BuiltinNiche } from "@/lib/mockData";
import { formatAbsolute } from "@/lib/formatters";
import { generateNiche } from "@/lib/aiNiche.functions";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";

export const Route = createFileRoute("/configuration")({
  head: () => ({ meta: [{ title: "Configuración · LeadFunnel" }] }),
  component: ConfigurationPage,
});

const SOURCE_META: Record<LeadSource, { icon: typeof MapPin; desc: string }> = {
  google_maps: { icon: MapPin, desc: "Búsquedas geolocalizadas de negocios locales" },
  rues: { icon: FileCheck2, desc: "Registro Único Empresarial y Social - empresas formales" },
  la_republica: { icon: Newspaper, desc: "Diario económico La República - empresas con tracción mediática" },
};

const NICHE_ICONS: Record<BuiltinNiche, typeof MapPin> = {
  restaurantes: Utensils,
  tecnologia: Cpu,
  salud: HeartPulse,
  retail: ShoppingBag,
  servicios: Wrench,
  construccion: HardHat,
  educacion: GraduationCap,
  finanzas: Landmark,
};

function useCountdown(target: number) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(t); }, []);
  const ms = Math.max(0, target - now);
  const m = Math.floor(ms / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function ConfigurationPage() {
  const sources = useLeadStore((s) => s.sources);
  const toggleSource = useLeadStore((s) => s.toggleSource);
  const niches = useLeadStore((s) => s.niches);
  const toggleNiche = useLeadStore((s) => s.toggleNiche);
  const nicheLabels = useLeadStore((s) => s.nicheLabels);
  const addCustomNiche = useLeadStore((s) => s.addCustomNiche);
  const scrapeLimit = useLeadStore((s) => s.scrapeLimit);
  const setScrapeLimit = useLeadStore((s) => s.setScrapeLimit);
  const leads = useLeadStore((s) => s.leads);
  const logs = useLeadStore((s) => s.scrapeLogs);
  const trigger = useLeadStore((s) => s.triggerScrape);
  const nextRunAt = useLeadStore((s) => s.nextRunAt);
  const setNextRunAt = useLeadStore((s) => s.setNextRunAt);
  const isRunning = useLeadStore((s) => s.isRunning);
  const setRunning = useLeadStore((s) => s.setRunning);
  const countdown = useCountdown(nextRunAt);

  const nicheCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    Object.keys(nicheLabels).forEach((n) => (counts[n] = 0));
    leads.forEach((l) => { counts[l.niche] = (counts[l.niche] ?? 0) + 1; });
    return counts;
  }, [leads, nicheLabels]);

  const [aiOpen, setAiOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<{ name: string; reason: string } | null>(null);

  const handleGenerateNiche = async () => {
    if (aiPrompt.trim().length < 3) {
      toast.error("Describe el cliente que buscas (mín. 3 caracteres)");
      return;
    }
    setAiLoading(true);
    setAiResult(null);
    try {
      const res = await generateNiche({ data: { description: aiPrompt } });
      setAiResult(res);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Error generando nicho");
    } finally {
      setAiLoading(false);
    }
  };

  const handleAcceptNiche = () => {
    if (!aiResult) return;
    addCustomNiche(aiResult.name);
    toast.success(`Nicho "${aiResult.name}" creado`);
    setAiOpen(false);
    setAiPrompt("");
    setAiResult(null);
  };

  const handleRunNow = () => {
    trigger();
    toast.success("Scraping ejecutado", { description: "Los nuevos leads aparecerán en el dashboard." });
    setNextRunAt(Date.now() + 5 * 60 * 1000);
  };

  const toggleRunning = () => {
    const next = !isRunning;
    setRunning(next);
    toast[next ? "success" : "info"](next ? "Automatización iniciada" : "Automatización detenida");
  };

  return (
    <div className="space-y-6 max-w-[1200px] mx-auto">
      <div>
        <h2 className="text-2xl font-bold">Fuentes de Leads</h2>
        <p className="text-sm text-muted-foreground mt-1">Activa o desactiva los scrapers automáticos. Se ejecutan cada 5 minutos.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {(Object.keys(SOURCE_LABELS) as LeadSource[]).map((src) => {
          const Icon = SOURCE_META[src].icon;
          const enabled = sources[src];
          return (
            <div key={src} className="rounded-xl border border-border bg-card p-5 shadow-sm flex items-start gap-4">
              <div className={`h-12 w-12 rounded-lg grid place-items-center ${enabled ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}`}>
                <Icon className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">{SOURCE_LABELS[src]}</h3>
                  <button
                    onClick={() => { toggleSource(src); toast.info(`${SOURCE_LABELS[src]} ${!enabled ? "activada" : "desactivada"}`); }}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${enabled ? "bg-primary" : "bg-muted-foreground/30"}`}
                  >
                    <span className={`inline-block h-5 w-5 rounded-full bg-white transition-transform shadow ${enabled ? "translate-x-5" : "translate-x-0.5"}`} />
                  </button>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{SOURCE_META[src].desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="rounded-xl border border-border bg-gradient-to-br from-primary to-primary-glow text-primary-foreground p-6 shadow-md">
          <div className="flex items-center gap-2 text-xs uppercase tracking-wider opacity-80">
            <Clock className="h-4 w-4" /> Próxima ejecución
          </div>
          <div className="mt-3 text-5xl font-bold tabular-nums">{isRunning ? countdown : "—"}</div>
          <div className="mt-2 text-xs opacity-80">
            Estado: <span className="font-semibold">{isRunning ? "En ejecución" : "Detenido"}</span>
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            <button
              onClick={toggleRunning}
              className="inline-flex items-center gap-2 rounded-lg bg-white text-primary hover:bg-white/90 px-4 py-2 text-sm font-semibold transition-colors"
            >
              {isRunning ? <><Pause className="h-4 w-4" /> Detener</> : <><Play className="h-4 w-4" /> Iniciar</>}
            </button>
            <button
              onClick={handleRunNow}
              className="inline-flex items-center gap-2 rounded-lg bg-white/15 hover:bg-white/25 backdrop-blur px-4 py-2 text-sm font-medium transition-colors"
            >
              <Play className="h-4 w-4" /> Ejecutar ahora
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 rounded-xl border border-border bg-card p-5 shadow-sm">
          <h3 className="text-sm font-semibold mb-3">Log de últimos scrapes</h3>
          {logs.length === 0 ? (
            <div className="text-sm text-muted-foreground py-8 text-center">No hay ejecuciones recientes.</div>
          ) : (
            <ul className="divide-y divide-border">
              {logs.map((l) => (
                <li key={l.id} className="flex items-center justify-between py-2.5 text-sm">
                  <div>
                    <span className="font-medium">{SOURCE_LABELS[l.source]}</span>
                    <span className="text-muted-foreground ml-2 tabular-nums">· {formatAbsolute(l.at)}</span>
                  </div>
                  <span className="text-success font-semibold tabular-nums">+{l.extracted} leads</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-sm font-semibold">Límite de scrapeo por ejecución</h3>
          <span className="text-2xl font-bold tabular-nums text-primary">{scrapeLimit}</span>
        </div>
        <p className="text-xs text-muted-foreground mb-3">Máximo de leads extraídos en cada ciclo automático o manual (1–100).</p>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={1}
            max={100}
            value={scrapeLimit}
            onChange={(e) => setScrapeLimit(Number(e.target.value))}
            className="flex-1 accent-primary"
          />
          <input
            type="number"
            min={1}
            max={100}
            value={scrapeLimit}
            onChange={(e) => setScrapeLimit(Number(e.target.value))}
            className="h-9 w-20 px-2 rounded-md border border-input bg-background text-sm tabular-nums"
          />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-primary" />
            <h2 className="text-2xl font-bold">Nichos</h2>
          </div>
          <button
            onClick={() => setAiOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-primary to-primary-glow text-primary-foreground px-4 py-2 text-sm font-semibold shadow-sm hover:opacity-95"
          >
            <Sparkles className="h-4 w-4" /> AI Insight
          </button>
        </div>
        <p className="text-sm text-muted-foreground mb-4">Selecciona los nichos visibles. Los leads de nichos desactivados quedan ocultos en el dashboard.</p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.keys(nicheLabels).map((n) => {
            const Icon = (NICHE_ICONS as Record<string, typeof MapPin>)[n] ?? Sparkles;
            const enabled = niches[n];
            const isCustom = !(n in NICHE_ICONS);
            return (
              <button
                key={n}
                onClick={() => { toggleNiche(n); toast.info(`${nicheLabels[n]} ${!enabled ? "visible" : "oculto"}`); }}
                className={`rounded-xl border p-4 text-left transition-all ${enabled ? "border-primary/40 bg-primary/5" : "border-border bg-card opacity-60"}`}
              >
                <div className="flex items-center justify-between">
                  <div className={`h-9 w-9 rounded-lg grid place-items-center ${enabled ? "bg-primary/15 text-primary" : "bg-muted text-muted-foreground"}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className={`h-4 w-4 rounded-full border ${enabled ? "bg-primary border-primary" : "border-muted-foreground/30"}`} />
                </div>
                <div className="mt-3 font-semibold text-sm flex items-center gap-1.5">
                  {nicheLabels[n]}
                  {isCustom && <span className="text-[9px] px-1 py-0.5 rounded bg-primary/15 text-primary uppercase tracking-wider">IA</span>}
                </div>
                <div className="text-xs text-muted-foreground tabular-nums">{nicheCounts[n] ?? 0} leads</div>
              </button>
            );
          })}
        </div>
      </div>

      <Dialog open={aiOpen} onOpenChange={setAiOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" /> AI Insight · Crear nicho
            </DialogTitle>
            <DialogDescription>
              Describe el cliente ideal que quieres buscar y la IA propondrá un nicho a la medida.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <textarea
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="Ej: Restaurantes veganos en Bogotá con menos de 20 empleados y presencia en Instagram"
              className="w-full min-h-[110px] rounded-md border border-input bg-background p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/40"
              maxLength={500}
              disabled={aiLoading}
            />
            <div className="text-xs text-muted-foreground text-right tabular-nums">{aiPrompt.length}/500</div>
            {aiResult && (
              <div className="rounded-lg border border-primary/30 bg-primary/5 p-4">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="text-xs uppercase tracking-wider text-primary font-semibold">Nicho propuesto</div>
                    <div className="text-lg font-bold mt-1">{aiResult.name}</div>
                    <p className="text-xs text-muted-foreground mt-1">{aiResult.reason}</p>
                  </div>
                  <button onClick={() => setAiResult(null)} className="text-muted-foreground hover:text-foreground" aria-label="Descartar">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
          <DialogFooter className="gap-2">
            {!aiResult ? (
              <button
                onClick={handleGenerateNiche}
                disabled={aiLoading}
                className="inline-flex items-center gap-2 rounded-lg bg-primary text-primary-foreground px-4 py-2 text-sm font-semibold disabled:opacity-50"
              >
                {aiLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                {aiLoading ? "Generando..." : "Generar nicho"}
              </button>
            ) : (
              <button
                onClick={handleAcceptNiche}
                className="inline-flex items-center gap-2 rounded-lg bg-success text-success-foreground px-4 py-2 text-sm font-semibold"
              >
                Añadir nicho
              </button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
