import { useEffect, useState } from "react";
import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, Settings, BarChart3, Radar, Bell, Play, Pause, Moon, Sun } from "lucide-react";
import { useLeadStore } from "@/store/leadStore";
import { useRealtimeSimulator } from "@/hooks/useRealtimeSimulator";
import { toast } from "sonner";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/configuration", label: "Configuración", icon: Settings, exact: false },
  { to: "/analytics", label: "Análisis", icon: BarChart3, exact: false },
];

export function AppLayout() {
  const hydrate = useLeadStore((s) => s.hydrate);
  const hydrated = useLeadStore((s) => s.hydrated);
  useEffect(() => { hydrate(); }, [hydrate]);
  useRealtimeSimulator();
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  const totalLeads = useLeadStore((s) => s.leads.length);
  const isRunning = useLeadStore((s) => s.isRunning);
  const setRunning = useLeadStore((s) => s.setRunning);

  const [theme, setTheme] = useState<"light" | "dark">("light");
  useEffect(() => {
    const saved = (localStorage.getItem("theme") as "light" | "dark" | null) ??
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    setTheme(saved);
  }, []);
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleRun = () => {
    const next = !isRunning;
    setRunning(next);
    toast[next ? "success" : "info"](next ? "Automatización iniciada" : "Automatización detenida");
  };

  return (
    <div className="min-h-screen flex bg-background text-foreground">
      <aside className="w-[220px] shrink-0 bg-sidebar text-sidebar-foreground border-r border-sidebar-border flex flex-col">
        <div className="px-5 py-6 flex items-center gap-2">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-primary to-primary-glow grid place-items-center">
            <Radar className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <div className="font-bold text-base leading-tight">LeadFunnel</div>
            <div className="text-[10px] uppercase tracking-wider text-sidebar-foreground/60">GTM Hackathon</div>
          </div>
        </div>
        <nav className="flex-1 px-3 space-y-1">
          {NAV.map((n) => {
            const active = n.exact ? pathname === n.to : pathname.startsWith(n.to);
            return (
              <Link
                key={n.to}
                to={n.to}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                  active ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium" : "text-sidebar-foreground/80 hover:bg-sidebar-accent/40"
                }`}
              >
                <n.icon className="h-4 w-4" />
                {n.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 mx-3 mb-4 rounded-lg bg-sidebar-accent/40 text-xs">
          <div className="text-sidebar-foreground/60">Leads en sistema</div>
          <div className="text-2xl font-bold mt-1">{totalLeads}</div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 border-b border-border bg-card/60 backdrop-blur flex items-center justify-between px-6">
          <div>
            <h1 className="text-lg font-semibold">Lead Funnel Automation</h1>
            <p className="text-xs text-muted-foreground">Búsqueda → Captura → Validación RUES → Scoring → Contacto</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="relative flex h-2 w-2">
                {isRunning && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-60" />}
                <span className={`relative inline-flex rounded-full h-2 w-2 ${isRunning ? "bg-success" : "bg-muted-foreground"}`} />
              </span>
              {isRunning ? "En vivo" : "Detenido"}
            </span>
            <button
              onClick={toggleRun}
              className={`inline-flex items-center gap-1.5 h-9 px-3 rounded-lg text-sm font-medium transition-colors ${
                isRunning ? "bg-destructive/10 text-destructive hover:bg-destructive/20" : "bg-success/15 text-success hover:bg-success/25"
              }`}
            >
              {isRunning ? <><Pause className="h-4 w-4" /> Detener</> : <><Play className="h-4 w-4" /> Iniciar</>}
            </button>
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              aria-label="Cambiar tema"
              className="h-9 w-9 grid place-items-center rounded-lg border border-border hover:bg-accent"
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <button className="h-9 w-9 grid place-items-center rounded-lg border border-border hover:bg-accent">
              <Bell className="h-4 w-4" />
            </button>
          </div>
        </header>
        <main className="flex-1 p-6 overflow-auto">
          {hydrated ? <Outlet /> : null}
        </main>
      </div>
    </div>
  );
}
