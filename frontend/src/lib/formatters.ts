export const formatNumber = (n: number) => new Intl.NumberFormat("en-US").format(n);
export const formatPercent = (n: number, digits = 1) => `${n.toFixed(digits)}%`;
export const formatRelative = (date: Date | string) => {
  const d = typeof date === "string" ? new Date(date) : date;
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return `hace ${Math.floor(diff)}s`;
  if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`;
  return `hace ${Math.floor(diff / 86400)}d`;
};
export const formatAbsolute = (date: Date | string) => {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
};
