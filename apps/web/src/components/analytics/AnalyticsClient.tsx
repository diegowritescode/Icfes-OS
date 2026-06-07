"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { apiFetch } from "@/lib/api";
import type { AreaAnalytics, TopicPriority } from "@/lib/types";
import { areaLabel, formatPercent } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { Card, CardTitle } from "@/components/ui/Card";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/State";

type ErrorRow = { error_type: string; count: number };

export function AnalyticsClient() {
  const [areas, setAreas] = useState<AreaAnalytics[]>([]);
  const [topics, setTopics] = useState<TopicPriority[]>([]);
  const [errors, setErrors] = useState<ErrorRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [areaData, topicData, errorData] = await Promise.all([
          apiFetch<AreaAnalytics[]>("/analytics/by-area"),
          apiFetch<TopicPriority[]>("/analytics/by-topic"),
          apiFetch<ErrorRow[]>("/analytics/errors")
        ]);
        setAreas(areaData);
        setTopics(topicData);
        setErrors(errorData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error cargando analitica");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  if (loading) return <LoadingState label="Cargando analitica" />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Analitica</h1>
        <p className="mt-1 text-sm text-slate-600">Precision, errores y retorno esperado por tema.</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardTitle>Intentos por area</CardTitle>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={areas.map((item) => ({ ...item, label: areaLabel(item.area) }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="attempts" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardTitle>Errores por tipo</CardTitle>
          {errors.length ? (
            <div className="mt-4 space-y-3">
              {errors.map((item) => (
                <div key={item.error_type}>
                  <div className="flex justify-between text-sm">
                    <span>{item.error_type}</span>
                    <span className="font-medium">{item.count}</span>
                  </div>
                  <div className="mt-1 h-2 rounded bg-slate-100">
                    <div className="h-2 rounded bg-rose-500" style={{ width: `${Math.min(100, item.count * 20)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="Aun no hay errores registrados." />
          )}
        </Card>
      </div>

      <Card>
        <CardTitle>Prioridad por tema</CardTitle>
        {topics.length ? (
          <div className="mt-4 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  <th className="py-2 pr-3">Tema</th>
                  <th className="py-2 pr-3">Area</th>
                  <th className="py-2 pr-3">Prioridad</th>
                  <th className="py-2 pr-3">Error</th>
                  <th className="py-2 pr-3">Mastery</th>
                  <th className="py-2 pr-3">Accion</th>
                </tr>
              </thead>
              <tbody>
                {topics.map((item) => (
                  <tr key={`${item.area}-${item.topic}`} className="border-t border-line">
                    <td className="py-2 pr-3 font-medium">{item.topic}</td>
                    <td className="py-2 pr-3">
                      <Badge area={item.area}>{areaLabel(item.area)}</Badge>
                    </td>
                    <td className="py-2 pr-3">{formatPercent(item.priority_score)}</td>
                    <td className="py-2 pr-3">{formatPercent(item.error_rate)}</td>
                    <td className="py-2 pr-3">{formatPercent(item.mastery_score)}</td>
                    <td className="py-2 pr-3">{item.interpretation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="Importa preguntas para calcular prioridades." />
        )}
      </Card>
    </div>
  );
}
