/**
 * Tipos reales de la API de Phylloleads
 * No son mocks - vienen directamente del backend
 */

// Categorías de scoring (no equidistante)
export type LeadCategory = 'A' | 'B' | 'C';

// Nichos disponibles
export type Niche = 
  | 'veterinarias' 
  | 'restaurantes' 
  | 'peluquerías' 
  | 'gimnasios' 
  | 'consultorios' 
  | string;

// Lead del API
export interface Lead {
  id: number;
  name: string;
  phone?: string;
  website?: string;
  address?: string;
  city: string;
  score: number;
  category: LeadCategory;
  niche: string;
  scoring_details?: {
    name: number;
    phone: number;
    website: number;
    address: number;
    email: number;
    company_size: number;
    active_status: number;
  };
  sent_at?: string;
  created_at?: string;
}

// Response de /api/scraper/next-lead
export interface NextLeadResponse {
  success: boolean;
  lead: Lead;
  queue_status: {
    niche: string;
    remaining: number;
    target: number;
    sent: number;
  };
}

// Request a /api/scraper/start
export interface StartScraperRequest {
  niches: string[];
  target_count: number;
  min_category?: 'A' | 'B' | 'C';
  max_concurrent?: number;
}

// Response de /api/scraper/start
export interface StartScraperResponse {
  success: boolean;
  message: string;
  niches: string[];
  target_count: number;
}

// Request a /api/scraper/submit-leads
export interface SubmitLeadsRequest {
  niche: string;
  leads: Array<{
    id: number | string;
    name: string;
    phone?: string;
    website?: string;
    address?: string;
    city: string;
  }>;
}

// Response de /api/scraper/submit-leads
export interface SubmitLeadsResponse {
  added: number;
  duplicates: number;
  queued: number;
}

// Response de /api/scraper/status
export interface ScraperStatusResponse {
  status: 'idle' | 'processing' | 'completed';
  niches?: Record<string, {
    target: number;
    sent: number;
    queued: number;
    complete: boolean;
  }>;
  started_at?: string;
  last_update?: string;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'scraper_started' | 'lead_accepted' | 'status_update' | 'new_lead_queued';
  data?: any;
  timestamp?: string;
}

// Labels para UI
export const NICHE_LABELS: Record<string, string> = {
  veterinarias: 'Veterinarias',
  restaurantes: 'Restaurantes',
  peluquerías: 'Peluquerías',
  gimnasios: 'Gimnasios',
  consultorios: 'Consultorios',
};

export const CATEGORY_COLORS: Record<LeadCategory, string> = {
  A: 'bg-green-100 text-green-800',
  B: 'bg-yellow-100 text-yellow-800',
  C: 'bg-red-100 text-red-800',
};

export const CATEGORY_LABELS: Record<LeadCategory, string> = {
  A: 'Excelente (85-100)',
  B: 'Bueno (60-84)',
  C: 'Aceptable (0-59)',
};
