"use client";

import { useState } from "react";
import { CalendarPlus } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { DailyPlan } from "@/lib/types";
import { areaLabel } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Field, inputClass } from "@/components/ui/Field";
import { EmptyState, ErrorState } from "@/components/ui/State";

export function StudyPlanClient() {
  const [minutes, setMinutes] = useState(120);
  const [area, setArea] = useState("");
  const [maxBlocks, setMaxBlocks] = useState(3);
  const [preference, setPreference] = useState("mixto");
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<DailyPlan>("/recommendations/daily-plan", {
        method: "POST",
        body: JSON.stringify({
          available_minutes: minutes,
          area: area || null,
          max_blocks: maxBlocks,
          preference
        })
      });
      setPlan(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo generar plan");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Plan diario</h1>
        <p className="mt-1 text-sm text-slate-600">Convierte prioridades y repasos vencidos en bloques concretos.</p>
      </div>

      <Card>
        <div className="grid gap-3 md:grid-cols-5">
          <Field label="Minutos">
            <input className={inputClass} type="number" min={30} max={480} value={minutes} onChange={(event) => setMinutes(Number(event.target.value))} />
          </Field>
          <Field label="Area">
            <select className={inputClass} value={area} onChange={(event) => setArea(event.target.value)}>
              <option value="">Auto</option>
              <option value="ciencias_naturales">Ciencias</option>
              <option value="matematicas">Matematicas</option>
              <option value="sociales_ciudadanas">Sociales</option>
              <option value="ingles">Ingles</option>
              <option value="lectura_critica">Lectura</option>
            </select>
          </Field>
          <Field label="Bloques max">
            <input className={inputClass} type="number" min={1} max={6} value={maxBlocks} onChange={(event) => setMaxBlocks(Number(event.target.value))} />
          </Field>
          <Field label="Preferencia">
            <select className={inputClass} value={preference} onChange={(event) => setPreference(event.target.value)}>
              <option value="mixto">Mixto</option>
              <option value="teoria">Teoria</option>
              <option value="practica">Practica</option>
              <option value="repaso">Repaso</option>
            </select>
          </Field>
          <div className="flex items-end">
            <Button className="w-full" onClick={generate} disabled={loading}>
              <CalendarPlus size={16} />
              Generar
            </Button>
          </div>
        </div>
      </Card>

      {error ? <ErrorState message={error} /> : null}

      {plan ? (
        <div className="grid gap-4">
          {plan.plan_json.blocks.map((block) => (
            <Card key={block.block}>
              <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
                <div>
                  <CardTitle>Bloque {block.block}</CardTitle>
                  <h2 className="mt-2 text-xl font-semibold">{block.topic}</h2>
                  <p className="mt-2 text-sm text-slate-600">{block.activity}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Badge area={block.area}>{areaLabel(block.area)}</Badge>
                  <Badge>{block.minutes} min</Badge>
                  <Badge>{block.suggested_questions} preguntas</Badge>
                </div>
              </div>
              <p className="mt-4 rounded bg-panel p-3 text-sm leading-6 text-slate-700">{block.reason}</p>
              {block.review_question_ids.length ? (
                <p className="mt-3 text-sm text-slate-500">Repasar vencidas: {block.review_question_ids.join(", ")}</p>
              ) : null}
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState message="Genera un plan despues de importar preguntas. Si aun no hay intentos, el plan usa prioridades estrategicas iniciales." />
      )}
    </div>
  );
}
