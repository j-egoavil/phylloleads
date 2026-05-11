import { useEffect, useRef } from 'react';
import { useLeadStore } from '@/store/leadStore';
import { getApiUrl } from '@/lib/apiConfig';

export function useFetchLeads() {
  const isRunning = useLeadStore((s) => s.isRunning);
  const addLead = useLeadStore((s) => s.addLead);
  const addCustomNiche = useLeadStore((s) => s.addCustomNiche);
  const niches = useLeadStore((s) => s.niches);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isRunning) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    const API_URL = getApiUrl();

    const fetchNextLead = async () => {
      try {
        const response = await fetch(`${API_URL}/api/scraper/next-lead`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        if (data.success && data.lead) {
          const lead = data.lead;
          const niche = lead.niche || 'desconocido';
          
          // Agregar niche dinámicamente si no existe
          if (!niches[niche]) {
            addCustomNiche(niche);
          }
          
          addLead({
            id: lead.id,
            name: lead.name,
            phone: lead.phone,
            website: lead.website,
            address: lead.address,
            city: lead.city,
            score: lead.score,
            category: lead.category,
            niche: niche,
            status: 'search',
            source: 'backend',
            createdAt: new Date().toISOString(),
            rues: undefined,
            totalLeads: 0,
          });
        }
      } catch (err) {
        console.error('Error fetching lead:', err);
      }
    };

    // Fetch inicial
    fetchNextLead();

    // Polling cada 1 segundo
    intervalRef.current = setInterval(fetchNextLead, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isRunning, addLead, addCustomNiche, niches]);
}
