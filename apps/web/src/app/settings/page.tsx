"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Card, CardTitle } from "@/components/ui/Card";
import { ErrorState, LoadingState } from "@/components/ui/State";

type Health = {
  status: string;
  app: string;
  environment: string;
  ai_configured: boolean;
  embeddings_enabled: boolean;
};

export default function SettingsPage() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Health>("/health").then(setHealth).catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!health) return <LoadingState label="Verificando configuracion" />;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Configuracion</h1>
        <p className="mt-1 text-sm text-slate-600">Estado local de API, IA y busqueda semantica.</p>
      </div>

      <Card>
        <CardTitle>Estado</CardTitle>
        <div className="mt-4 grid gap-3 text-sm md:grid-cols-2">
          <div className="rounded border border-line p-3">
            <div className="text-slate-500">API</div>
            <div className="mt-1 font-medium">{health.status}</div>
          </div>
          <div className="rounded border border-line p-3">
            <div className="text-slate-500">Ambiente</div>
            <div className="mt-1 font-medium">{health.environment}</div>
          </div>
          <div className="rounded border border-line p-3">
            <div className="text-slate-500">IA</div>
            <div className="mt-2">
              <Badge>{health.ai_configured ? "Configurada" : "Fallback manual activo"}</Badge>
            </div>
          </div>
          <div className="rounded border border-line p-3">
            <div className="text-slate-500">Embeddings</div>
            <div className="mt-2">
              <Badge>{health.embeddings_enabled ? "Activos" : "Busqueda por texto/tema"}</Badge>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <CardTitle>Variables utiles</CardTitle>
        <pre className="mt-4 overflow-auto rounded bg-ink p-4 text-xs leading-6 text-white">
{`OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AI_PROVIDER=openai
ENABLE_EMBEDDINGS=false
NEXT_PUBLIC_API_URL=http://localhost:8000`}
        </pre>
      </Card>
    </div>
  );
}
