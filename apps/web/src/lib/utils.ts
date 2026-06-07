import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatPercent(value: number | null | undefined) {
  return `${Math.round((value ?? 0) * 100)}%`;
}

export function areaLabel(area: string) {
  const labels: Record<string, string> = {
    ciencias_naturales: "Ciencias",
    matematicas: "Matematicas",
    sociales_ciudadanas: "Sociales",
    lectura_critica: "Lectura",
    ingles: "Ingles"
  };
  return labels[area] ?? area;
}
