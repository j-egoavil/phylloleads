export type LeadSource = "google_maps" | "rues" | "la_republica";
export type LeadStatus = "search" | "captured" | "validating" | "scored" | "contacted" | "discarded" | "error";
export type LeadCategory = "A" | "B" | "C";
export type BuiltinNiche =
  | "restaurantes"
  | "tecnologia"
  | "salud"
  | "retail"
  | "servicios"
  | "construccion"
  | "educacion"
  | "finanzas";
export type LeadNiche = BuiltinNiche | string;

export interface Lead {
  id: string;
  name: string;
  company: string;
  nit?: string;
  phone?: string;
  email?: string;
  address?: string;
  source: LeadSource;
  status: LeadStatus;
  score: number;
  category: LeadCategory;
  niche: LeadNiche;
  createdAt: string;
  rues?: { validated: boolean; registrationDate?: string; matricula?: string };
  history: { phase: LeadStatus; at: string }[];
}

const COMPANIES = ["Café Andino SAS", "Tech Bogotá", "Distribuciones Norte", "Gastro Latam", "FinTech Colombia", "Logística Pacífico", "Inversiones El Sol", "Agro Valle SAS", "Constructora Aurora", "Estudio Digital MX", "Salud Integral", "Transportes Caribe", "EcoMercado", "BlueWave Studios", "Marketing 360", "Comercial Andes", "Soluciones IT", "Gourmet House", "Boutique Norte", "Consultora GTM"];
const NAMES = ["María González", "Carlos Pérez", "Ana Rodríguez", "Luis Torres", "Sofía Ramírez", "Diego Morales", "Camila Vargas", "Andrés López", "Valentina Ruiz", "Sebastián Díaz", "Paula Martínez", "Jorge Silva", "Daniela Castro", "Felipe Mejía", "Isabella Rojas"];
const SOURCES: LeadSource[] = ["google_maps", "rues", "la_republica"];
const STATUSES: LeadStatus[] = ["search", "captured", "validating", "scored", "contacted", "discarded", "error"];
const NICHES: BuiltinNiche[] = ["restaurantes", "tecnologia", "salud", "retail", "servicios", "construccion", "educacion", "finanzas"];

function inferNiche(company: string): BuiltinNiche {
  const c = company.toLowerCase();
  if (/(café|gastro|gourmet|mercado)/.test(c)) return "restaurantes";
  if (/(tech|it|digital|studios|fintech)/.test(c)) return "tecnologia";
  if (/(salud)/.test(c)) return "salud";
  if (/(boutique|comercial|distribuciones)/.test(c)) return "retail";
  if (/(constructora)/.test(c)) return "construccion";
  if (/(inversiones|fintech|finanzas)/.test(c)) return "finanzas";
  if (/(consultora|marketing|logística|transportes|estudio|soluciones)/.test(c)) return "servicios";
  if (/(agro|eco)/.test(c)) return "retail";
  return NICHES[Math.floor(Math.random() * NICHES.length)];
}

const rand = <T>(arr: T[]) => arr[Math.floor(Math.random() * arr.length)];
const randInt = (a: number, b: number) => Math.floor(Math.random() * (b - a + 1)) + a;

export function generateLead(idx: number, hoursAgo = 0): Lead {
  const score = randInt(20, 99);
  const category: LeadCategory = score >= 75 ? "A" : score >= 50 ? "B" : "C";
  const status = rand(STATUSES);
  const createdAt = new Date(Date.now() - hoursAgo * 3600_000 - randInt(0, 60) * 60_000).toISOString();
  const company = rand(COMPANIES);
  const missing = Math.random();
  return {
    id: `lead_${idx}_${Math.random().toString(36).slice(2, 8)}`,
    name: rand(NAMES),
    company,
    nit: missing < 0.15 ? undefined : `${randInt(800, 999)}.${randInt(100, 999)}.${randInt(100, 999)}-${randInt(0, 9)}`,
    phone: missing < 0.2 ? undefined : `+57 30${randInt(0, 9)} ${randInt(100, 999)} ${randInt(1000, 9999)}`,
    email: missing < 0.1 ? undefined : `contacto@${company.toLowerCase().replace(/[^a-z]/g, "")}.co`,
    address: missing < 0.25 ? undefined : `Cra ${randInt(1, 100)} #${randInt(1, 100)}-${randInt(1, 99)}, Bogotá`,
    source: rand(SOURCES),
    status,
    score,
    category,
    niche: inferNiche(company),
    createdAt,
    rues: Math.random() > 0.3 ? { validated: Math.random() > 0.2, registrationDate: new Date(Date.now() - randInt(365, 3650) * 86400_000).toISOString(), matricula: `${randInt(100000, 999999)}` } : undefined,
    history: [
      { phase: "search", at: new Date(Date.now() - hoursAgo * 3600_000 - 3000_000).toISOString() },
      { phase: "captured", at: new Date(Date.now() - hoursAgo * 3600_000 - 2000_000).toISOString() },
      { phase: "validating", at: new Date(Date.now() - hoursAgo * 3600_000 - 1000_000).toISOString() },
      { phase: "scored", at: createdAt },
    ],
  };
}

export const seedLeads = (): Lead[] => Array.from({ length: 84 }, (_, i) => generateLead(i, Math.random() * 48));

export const SOURCE_LABELS: Record<LeadSource, string> = {
  google_maps: "Google Maps",
  rues: "RUES",
  la_republica: "La República",
};

export const STATUS_LABELS: Record<LeadStatus, string> = {
  search: "Búsqueda",
  captured: "Capturado",
  validating: "Validando RUES",
  scored: "Scoreado",
  contacted: "Contactado",
  discarded: "Descartado",
  error: "Error",
};

export const NICHE_LABELS: Record<BuiltinNiche, string> = {
  restaurantes: "Restaurantes",
  tecnologia: "Tecnología",
  salud: "Salud",
  retail: "Retail",
  servicios: "Servicios",
  construccion: "Construcción",
  educacion: "Educación",
  finanzas: "Finanzas",
};
