import { useEffect } from "react";
import { toast } from "sonner";
import { useLeadStore } from "@/store/leadStore";
import { generateLead, SOURCE_LABELS } from "@/lib/mockData";

/** Simulates Socket.io events: leads:created, queue:progress, metrics:updated */
export function useRealtimeSimulator() {
  const addLead = useLeadStore((s) => s.addLead);
  const setQueueProgress = useLeadStore((s) => s.setQueueProgress);
  const isRunning = useLeadStore((s) => s.isRunning);

  useEffect(() => {
    if (!isRunning) return;
    const leadInterval = setInterval(() => {
      const lead = generateLead(Date.now(), 0);
      addLead(lead);
      if (Math.random() > 0.7) {
        toast.success(`Nuevo lead: ${lead.company}`, {
          description: `Fuente: ${SOURCE_LABELS[lead.source]} · Score ${lead.score}`,
        });
      }
    }, 8000);

    const queueInterval = setInterval(() => {
      setQueueProgress(Math.floor(Math.random() * 100));
    }, 3000);

    return () => {
      clearInterval(leadInterval);
      clearInterval(queueInterval);
    };
  }, [addLead, setQueueProgress, isRunning]);
}
