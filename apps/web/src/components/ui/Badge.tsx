import { cn } from "@/lib/utils";

const areaStyles: Record<string, string> = {
  ciencias_naturales: "bg-emerald-100 text-emerald-800",
  matematicas: "bg-blue-100 text-blue-800",
  sociales_ciudadanas: "bg-amber-100 text-amber-900",
  lectura_critica: "bg-slate-100 text-slate-800",
  ingles: "bg-cyan-100 text-cyan-800"
};

export function Badge({ children, area }: { children: React.ReactNode; area?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded px-2 py-1 text-xs font-medium",
        area ? areaStyles[area] ?? "bg-slate-100 text-slate-800" : "bg-slate-100 text-slate-800"
      )}
    >
      {children}
    </span>
  );
}
