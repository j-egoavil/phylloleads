import { create } from "zustand";
import { NICHE_LABELS, type Lead, type LeadNiche, type LeadSource, type LeadStatus } from "@/lib/mockData";

interface Filters {
  search: string;
  status: LeadStatus | "all";
  source: LeadSource | "all";
  category: "A" | "B" | "C" | "all";
}

type SourceConfig = Record<LeadSource, boolean>;

type NicheConfig = Record<string, boolean>;
type NicheLabels = Record<string, string>;

interface ScrapeLog { id: string; source: LeadSource; at: string; extracted: number; }

interface LeadState {
  leads: Lead[];
  filters: Filters;
  selectedLeadId: string | null;
  sources: SourceConfig;
  niches: NicheConfig;
  nicheLabels: NicheLabels;
  scrapeLimit: number;
  scrapeLogs: ScrapeLog[];
  queueProgress: number;
  nextRunAt: number;
  isRunning: boolean;
  hydrated: boolean;
  setFilter: <K extends keyof Filters>(k: K, v: Filters[K]) => void;
  selectLead: (id: string | null) => void;
  toggleSource: (s: LeadSource) => void;
  toggleNiche: (n: LeadNiche) => void;
  addCustomNiche: (label: string) => string;
  setScrapeLimit: (n: number) => void;
  addLead: (lead: Lead) => void;
  updateLead: (id: string, patch: Partial<Lead>) => void;
  pushScrapeLog: (log: ScrapeLog) => void;
  setQueueProgress: (n: number) => void;
  setNextRunAt: (t: number) => void;
  triggerScrape: () => void;
  setRunning: (v: boolean) => void;
  hydrate: () => void;
}

export const useLeadStore = create<LeadState>((set, get) => ({
  leads: [],
  filters: { search: "", status: "all", source: "all", category: "all" },
  selectedLeadId: null,
  sources: { google_maps: true, rues: true, la_republica: true },
  niches: {
    restaurantes: true,
    tecnologia: true,
    salud: true,
    retail: true,
    servicios: true,
    construccion: true,
    educacion: true,
    finanzas: true,
  },
  nicheLabels: { ...NICHE_LABELS },
  scrapeLimit: 20,
  scrapeLogs: [],
  queueProgress: 0,
  nextRunAt: 0,
  isRunning: false,
  hydrated: false,
  setFilter: (k, v) => set((s) => ({ filters: { ...s.filters, [k]: v } })),
  selectLead: (id) => set({ selectedLeadId: id }),
  toggleSource: (s) => set((st) => ({ sources: { ...st.sources, [s]: !st.sources[s] } })),
  toggleNiche: (n) => set((st) => ({ niches: { ...st.niches, [n]: !st.niches[n] } })),
  addCustomNiche: (label) => {
    const key = label
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 40) || `nicho_${Date.now()}`;
    set((st) => ({
      niches: { ...st.niches, [key]: true },
      nicheLabels: { ...st.nicheLabels, [key]: label.trim() },
    }));
    return key;
  },
  setScrapeLimit: (n) => set({ scrapeLimit: Math.max(1, Math.min(100, Math.floor(n))) }),
  addLead: (lead) => set((st) => ({ leads: [lead, ...st.leads].slice(0, 500) })),
  updateLead: (id, patch) => set((st) => ({ leads: st.leads.map((l) => (l.id === id ? { ...l, ...patch } : l)) })),
  pushScrapeLog: (log) => set((st) => ({ scrapeLogs: [log, ...st.scrapeLogs].slice(0, 20) })),
  setQueueProgress: (n) => set({ queueProgress: n }),
  setNextRunAt: (t) => set({ nextRunAt: t }),
  setRunning: (v) => set({ isRunning: v }),
  hydrate: () => {
    if (get().hydrated) return;
    set({
      leads: [],
      scrapeLogs: [],
      queueProgress: 0,
      nextRunAt: 0,
      hydrated: true,
    });
  },
  triggerScrape: () => {
    // Mock data generation disabled. Use API integration instead.
    // See: useLeadScraper hook for real API data
  },
}));
