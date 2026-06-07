"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { apiFetch } from "@/lib/api";
import type { AreaAnalytics, Overview, TopicPriority } from "@/lib/types";
import { areaLabel, formatPercent } from "@/lib/utils";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { Card, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/State";

export function DashboardClient() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [areas, setAreas] = useState<AreaAnalytics[]>([]);
  const [priorities, setPriorities] = useState<TopicPriority[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [overviewData, areaData, priorityData] = await Promise.all([
        apiFetch<Overview>("/analytics/overview"),
        apiFetch<AreaAnalytics[]>("/analytics/by-area"),
        apiFetch<TopicPriority[]>("/analytics/priority-topics")
      ]);
      setOverview(overviewData);
      setAreas(areaData);
      setPriorities(priorityData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando dashboard");
    } finally {
      setLoading(false);
    }
  }

  async function importSample() {
    await apiFetch("/documents/import-sample", { method: "POST" });
    await load();
  }

  useEffect(() => {
    void load();
  }, []);

  if (loading) return <LoadingState label="Cargando dashboard" />;
  if (error) return <ErrorState message={error} />;
  if (!overview) return <EmptyState message="No hay datos todavia." />;

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-600">{overview.recommendation_today}</p>
        </div>
        <Button variant="secondary" onClick={importSample}>
          Importar sample
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Preguntas" value={overview.total_questions} detail="Banco importado" />
        <MetricCard title="Respondidas" value={overview.answered_questions} detail={`${overview.total_attempts} intentos`} />
        <MetricCard title="Precision global" value={formatPercent(overview.global_accuracy)} detail="Sobre intentos" />
        <MetricCard title="Repasos vencidos" value={overview.due_review_count} detail="Repeticion espaciada" />
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="min-h-80">
          <CardTitle>Precision por area</CardTitle>
          {areas.length ? (
            <div className="mt-4 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={areas.map((item) => ({ ...item, label: areaLabel(item.area), pct: Math.round(item.accuracy * 100) }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="pct" fill="#059669" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState message="Importa preguntas y registra intentos para ver precision por area." />
          )}
        </Card>

        <Card>
          <CardTitle>Top temas prioritarios</CardTitle>
          <div className="mt-4 space-y-3">
            {priorities.slice(0, 8).map((item) => (
              <div key={`${item.area}-${item.topic}`} className="rounded border border-line p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-medium">{item.topic}</div>
                    <div className="mt-1 text-xs text-slate-500">{item.interpretation}</div>
                  </div>
                  <Badge area={item.area}>{areaLabel(item.area)}</Badge>
                </div>
                <div className="mt-3 h-2 rounded bg-slate-100">
                  <div className="h-2 rounded bg-emerald-600" style={{ width: `${Math.round(item.priority_score * 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card>
        <CardTitle>Estado de IA</CardTitle>
        <div className="mt-3 flex flex-wrap gap-2 text-sm">
          <Badge>{overview.ai_configured ? "IA configurada" : "IA no configurada"}</Badge>
          <Badge>{overview.embeddings_enabled ? "Embeddings activos" : "Busqueda fallback"}</Badge>
        </div>
      </Card>
    </div>
  );
}
