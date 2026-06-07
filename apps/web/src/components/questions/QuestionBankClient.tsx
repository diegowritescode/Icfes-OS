"use client";

import { useEffect, useMemo, useState } from "react";
import { RefreshCw, Save, Search } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { Question } from "@/lib/types";
import { areaLabel } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Field, inputClass } from "@/components/ui/Field";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/State";

const areas = ["", "ciencias_naturales", "matematicas", "sociales_ciudadanas", "ingles", "lectura_critica"];

export function QuestionBankClient() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selected, setSelected] = useState<Question | null>(null);
  const [area, setArea] = useState("");
  const [search, setSearch] = useState("");
  const [topic, setTopic] = useState("");
  const [subarea, setSubarea] = useState("");
  const [difficulty, setDifficulty] = useState(3);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (area) params.set("area", area);
    if (search) params.set("search", search);
    params.set("limit", "100");
    return params.toString();
  }, [area, search]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<Question[]>(`/questions?${query}`);
      setQuestions(data);
      if (!selected && data.length) setSelected(data[0]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando preguntas");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  useEffect(() => {
    setTopic(selected?.classification?.topic ?? "");
    setSubarea(selected?.classification?.subarea ?? "");
    setDifficulty(selected?.classification?.difficulty ?? 3);
  }, [selected]);

  async function classifySelected() {
    if (!selected) return;
    setSaving(true);
    try {
      await apiFetch(`/questions/${selected.id}/classify`, { method: "POST" });
      await load();
    } finally {
      setSaving(false);
    }
  }

  async function saveClassification() {
    if (!selected) return;
    setSaving(true);
    try {
      const updated = await apiFetch<Question>(`/questions/${selected.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          classification: {
            area: selected.area,
            subarea,
            topic,
            difficulty,
            subtopic: selected.classification?.subtopic ?? null,
            competence: selected.classification?.competence ?? "manual",
            skill: selected.classification?.skill ?? "manual",
            concepts: selected.classification?.concepts_json ?? [],
            keywords: selected.classification?.keywords_json ?? [],
            likely_error_types: selected.classification?.likely_error_types_json ?? [],
            confidence: 0.9,
            classified_by: "manual"
          }
        })
      });
      setSelected(updated);
      setQuestions((items) => items.map((item) => (item.id === updated.id ? updated : item)));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Banco de preguntas</h1>
        <p className="mt-1 text-sm text-slate-600">Filtra, revisa y corrige clasificaciones manualmente.</p>
      </div>

      <Card>
        <div className="grid gap-3 md:grid-cols-[220px_1fr_auto]">
          <Field label="Area">
            <select className={inputClass} value={area} onChange={(event) => setArea(event.target.value)}>
              {areas.map((item) => (
                <option key={item} value={item}>
                  {item ? areaLabel(item) : "Todas"}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Buscar texto">
            <div className="relative">
              <Search className="absolute left-3 top-3 text-slate-400" size={16} />
              <input className={`${inputClass} w-full pl-9`} value={search} onChange={(event) => setSearch(event.target.value)} />
            </div>
          </Field>
          <div className="flex items-end">
            <Button variant="secondary" onClick={load}>
              <RefreshCw size={16} />
            </Button>
          </div>
        </div>
      </Card>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardTitle>Listado</CardTitle>
          <div className="mt-3 max-h-[650px] overflow-auto">
            {questions.length ? (
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-white text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-2 pr-3">ID</th>
                    <th className="py-2 pr-3">Area</th>
                    <th className="py-2 pr-3">Tema</th>
                    <th className="py-2 pr-3">Pregunta</th>
                  </tr>
                </thead>
                <tbody>
                  {questions.map((question) => (
                    <tr
                      key={question.id}
                      className="cursor-pointer border-t border-line hover:bg-panel"
                      onClick={() => setSelected(question)}
                    >
                      <td className="py-2 pr-3 font-medium">{question.id}</td>
                      <td className="py-2 pr-3">
                        <Badge area={question.area}>{areaLabel(question.area)}</Badge>
                      </td>
                      <td className="py-2 pr-3">{question.classification?.topic ?? "sin_clasificar"}</td>
                      <td className="line-clamp-2 py-2 pr-3 text-slate-600">{question.statement}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState message="No hay preguntas con estos filtros." />
            )}
          </div>
        </Card>

        <Card>
          <CardTitle>Detalle y clasificacion</CardTitle>
          {selected ? (
            <div className="mt-4 space-y-4">
              <div className="flex flex-wrap gap-2">
                <Badge area={selected.area}>{areaLabel(selected.area)}</Badge>
                <Badge>{selected.year ?? "sin ano"}</Badge>
                <Badge>Dificultad {selected.classification?.difficulty ?? "n/a"}</Badge>
              </div>
              <p className="text-base leading-7">{selected.statement}</p>
              <div className="grid gap-2 text-sm">
                {(["A", "B", "C", "D"] as const).map((letter) => {
                  const key = `option_${letter.toLowerCase()}` as keyof Question;
                  return (
                    <div key={letter} className="rounded border border-line p-3">
                      <span className="font-semibold">{letter}.</span> {String(selected[key])}
                    </div>
                  );
                })}
              </div>
              <div className="rounded bg-emerald-50 p-3 text-sm text-emerald-900">
                Correcta: {selected.correct_answer}. {selected.explanation}
              </div>
              <div className="grid gap-3 md:grid-cols-3">
                <Field label="Subarea">
                  <input className={inputClass} value={subarea} onChange={(event) => setSubarea(event.target.value)} />
                </Field>
                <Field label="Tema">
                  <input className={inputClass} value={topic} onChange={(event) => setTopic(event.target.value)} />
                </Field>
                <Field label="Dificultad">
                  <input className={inputClass} type="number" min={1} max={5} value={difficulty} onChange={(event) => setDifficulty(Number(event.target.value))} />
                </Field>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button onClick={saveClassification} disabled={saving}>
                  <Save size={16} />
                  Guardar manual
                </Button>
                <Button variant="secondary" onClick={classifySelected} disabled={saving}>
                  Clasificar con IA/fallback
                </Button>
              </div>
            </div>
          ) : (
            <EmptyState message="Selecciona una pregunta para ver detalles." />
          )}
        </Card>
      </div>
    </div>
  );
}
