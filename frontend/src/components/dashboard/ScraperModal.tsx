import { useState } from "react";
import { X, Play, Loader2 } from "lucide-react";

interface ScraperModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (niches: string[], targetCount: number) => void;
  isLoading?: boolean;
}

const POPULAR_NICHES = [
  "veterinarias",
  "restaurantes",
  "peluquería",
  "farmacia",
  "electricista",
  "plomería",
  "abogado",
  "dentista",
  "psicólogo",
  "fisioterapeuta",
];

export function ScraperModal({ isOpen, onClose, onSubmit, isLoading }: ScraperModalProps) {
  const [selectedNiches, setSelectedNiches] = useState<string[]>([]);
  const [customNiche, setCustomNiche] = useState("");
  const [targetCount, setTargetCount] = useState(10);

  if (!isOpen) return null;

  const handleAddCustom = () => {
    if (customNiche.trim() && !selectedNiches.includes(customNiche.trim())) {
      setSelectedNiches([...selectedNiches, customNiche.trim()]);
      setCustomNiche("");
    }
  };

  const handleSubmit = () => {
    if (selectedNiches.length > 0) {
      onSubmit(selectedNiches, targetCount);
      setSelectedNiches([]);
      setTargetCount(10);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card border border-border rounded-lg shadow-lg max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold">Iniciar Búsqueda de Leads</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-muted rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Target Count */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Leads objetivo por nicho
            </label>
            <input
              type="number"
              min="1"
              max="100"
              value={targetCount}
              onChange={(e) => setTargetCount(Math.max(1, parseInt(e.target.value) || 10))}
              className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Popular Niches */}
          <div>
            <label className="block text-sm font-medium mb-2">Nichos populares</label>
            <div className="grid grid-cols-2 gap-2">
              {POPULAR_NICHES.map((niche) => (
                <button
                  key={niche}
                  onClick={() => {
                    if (selectedNiches.includes(niche)) {
                      setSelectedNiches(selectedNiches.filter((n) => n !== niche));
                    } else {
                      setSelectedNiches([...selectedNiches, niche]);
                    }
                  }}
                  className={`px-3 py-2 rounded-md border text-xs font-medium transition-colors ${
                    selectedNiches.includes(niche)
                      ? "bg-primary text-primary-foreground border-primary"
                      : "border-input bg-background hover:bg-muted"
                  }`}
                >
                  {niche}
                </button>
              ))}
            </div>
          </div>

          {/* Custom Niche */}
          <div>
            <label className="block text-sm font-medium mb-2">Agregar nicho personalizado</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="ej: carpintería"
                value={customNiche}
                onChange={(e) => setCustomNiche(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddCustom()}
                className="flex-1 px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
              <button
                onClick={handleAddCustom}
                className="px-3 py-2 rounded-md bg-muted hover:bg-muted/80 text-sm font-medium transition-colors"
              >
                Agregar
              </button>
            </div>
          </div>

          {/* Selected Niches */}
          {selectedNiches.length > 0 && (
            <div>
              <label className="block text-sm font-medium mb-2">Nichos seleccionados</label>
              <div className="flex flex-wrap gap-2">
                {selectedNiches.map((niche) => (
                  <div
                    key={niche}
                    className="px-3 py-1 rounded-full bg-primary/20 text-primary text-xs font-medium flex items-center gap-2"
                  >
                    {niche}
                    <button
                      onClick={() => setSelectedNiches(selectedNiches.filter((n) => n !== niche))}
                      className="hover:opacity-70"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-2 p-4 border-t border-border">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-md border border-input hover:bg-muted transition-colors text-sm font-medium"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={selectedNiches.length === 0 || isLoading}
            className="flex-1 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Buscando...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Iniciar búsqueda
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
