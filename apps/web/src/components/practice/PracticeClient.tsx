"use client";

import { useEffect, useState } from "react";
import { Clock, RotateCcw } from "lucide-react";
import { apiFetch } from "@/lib/api";
import type { Attempt, Question } from "@/lib/types";
import { areaLabel } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Field, inputClass } from "@/components/ui/Field";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/State";

const errorTypes = [
  "no_sabia_concepto",
  "formula_olvidada",
  "lectura_apresurada",
  "interprete_mal_grafica",
  "calculo_mal",
  "confundi_conceptos",
  "cai_en_distractor",
  "me_falto_contexto_colombia",
  "dude_entre_dos",
  "tiempo_excesivo",
  "otro"
];

export function PracticeClient() {
  const [question, setQuestion] = useState<Question | null>(null);
  const [mode, setMode] = useState("adaptive");
  const [area, setArea] = useState("");
  const [selected, setSelected] = useState<"A" | "B" | "C" | "D" | "">("");
  const [confidence, setConfidence] = useState(3);
  const [errorType, setErrorType] = useState("no_sabia_concepto");
  const [seconds, setSeconds] = useState(0);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadNext() {
    setLoading(true);
    setError(null);
    setAttempt(null);
    setAiExplanation(null);
    setSelected("");
    setSeconds(0);
    const params = new URLSearchParams({ mode });
    if (area) params.set("area", area);
    try {
      const data = await apiFetch<Question>(`/practice/next?${params.toString()}`);
      setQuestion(data);
    } catch (err) {
      setQuestion(null);
      setError(err instanceof Error ? err.message : "No se pudo cargar pregunta");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadNext();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (attempt) return;
    const timer = window.setInterval(() => setSeconds((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [attempt]);

  async function submit() {
    if (!question || !selected) return;
    const isWrong = selected !== question.correct_answer;
    const data = await apiFetch<Attempt>("/practice/attempt", {
      method: "POST",
      body: JSON.stringify({
        question_id: question.id,
        selected_answer: selected,
        confidence,
        time_seconds: seconds,
        error_type: isWrong ? errorType : null
      })
    });
    setAttempt(data);
  }

  async function explainWithAi() {
    if (!question || !selected) return;
    const result = await apiFetch<{ used_ai: boolean; explanation: string }>("/tutor/explain-error", {
      method: "POST",
      body: JSON.stringify({
        question_id: question.id,
        user_answer: selected,
        error_type: attempt?.error_type ?? errorType
      })
    });
    setAiExplanation(result.explanation);
  }

  const isWrong = Boolean(question && selected && selected !== question.correct_answer);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Practica</h1>
        <p className="mt-1 text-sm text-slate-600">Resuelve, registra confianza y convierte errores en datos.</p>
      </div>

      <Card>
        <div className="grid gap-3 md:grid-cols-[180px_220px_auto]">
          <Field label="Modo">
            <select className={inputClass} value={mode} onChange={(event) => setMode(event.target.value)}>
              <option value="adaptive">Adaptativa</option>
              <option value="review">Repaso vencido</option>
              <option value="area">Por area</option>
            </select>
          </Field>
          <Field label="Area opcional">
            <select className={inputClass} value={area} onChange={(event) => setArea(event.target.value)}>
              <option value="">Auto</option>
              <option value="ciencias_naturales">Ciencias</option>
              <option value="matematicas">Matematicas</option>
              <option value="sociales_ciudadanas">Sociales</option>
              <option value="ingles">Ingles</option>
              <option value="lectura_critica">Lectura</option>
            </select>
          </Field>
          <div className="flex items-end">
            <Button variant="secondary" onClick={loadNext}>
              <RotateCcw size={16} />
              Cargar
            </Button>
          </div>
        </div>
      </Card>

      {loading ? <LoadingState label="Buscando pregunta" /> : null}
      {error ? <ErrorState message={error} /> : null}

      {question ? (
        <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap gap-2">
                <Badge area={question.area}>{areaLabel(question.area)}</Badge>
                <Badge>{question.classification?.topic ?? "sin_clasificar"}</Badge>
                <Badge>D{question.classification?.difficulty ?? 3}</Badge>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Clock size={16} />
                {seconds}s
              </div>
            </div>
            <p className="mt-5 text-lg leading-8">{question.statement}</p>
            <div className="mt-5 grid gap-3">
              {(["A", "B", "C", "D"] as const).map((letter) => {
                const key = `option_${letter.toLowerCase()}` as keyof Question;
                const active = selected === letter;
                const showCorrect = attempt && question.correct_answer === letter;
                const showWrong = attempt && selected === letter && selected !== question.correct_answer;
                return (
                  <button
                    key={letter}
                    disabled={Boolean(attempt)}
                    className={`focus-ring rounded border p-4 text-left text-sm transition ${
                      showCorrect
                        ? "border-emerald-400 bg-emerald-50"
                        : showWrong
                          ? "border-rose-300 bg-rose-50"
                          : active
                            ? "border-blue-400 bg-blue-50"
                            : "border-line bg-white hover:bg-panel"
                    }`}
                    onClick={() => setSelected(letter)}
                  >
                    <span className="font-semibold">{letter}.</span> {String(question[key])}
                  </button>
                );
              })}
            </div>
          </Card>

          <Card>
            <CardTitle>Registro</CardTitle>
            <div className="mt-4 space-y-4">
              <Field label="Confianza">
                <div className="grid grid-cols-5 gap-2">
                  {[1, 2, 3, 4, 5].map((value) => (
                    <button
                      key={value}
                      className={`focus-ring rounded border py-2 text-sm ${confidence === value ? "border-emerald-600 bg-emerald-50" : "border-line bg-white"}`}
                      onClick={() => setConfidence(value)}
                    >
                      {value}
                    </button>
                  ))}
                </div>
              </Field>
              {isWrong && !attempt ? (
                <Field label="Tipo de error">
                  <select className={inputClass} value={errorType} onChange={(event) => setErrorType(event.target.value)}>
                    {errorTypes.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </Field>
              ) : null}
              <Button className="w-full" disabled={!selected || Boolean(attempt)} onClick={submit}>
                Guardar respuesta
              </Button>
              {attempt ? (
                <div className={`rounded p-3 text-sm ${attempt.is_correct ? "bg-emerald-50 text-emerald-900" : "bg-rose-50 text-rose-900"}`}>
                  {attempt.is_correct ? "Correcta." : `Incorrecta. Correcta: ${attempt.correct_answer}.`}
                  <div className="mt-2 text-slate-700">{question.explanation}</div>
                </div>
              ) : null}
              {attempt && !attempt.is_correct ? (
                <Button variant="secondary" className="w-full" onClick={explainWithAi}>
                  Explicarme con IA
                </Button>
              ) : null}
              {aiExplanation ? <div className="rounded border border-line bg-panel p-3 text-sm leading-6">{aiExplanation}</div> : null}
              {attempt ? (
                <Button className="w-full" onClick={loadNext}>
                  Siguiente pregunta
                </Button>
              ) : null}
            </div>
          </Card>
        </div>
      ) : !loading ? (
        <EmptyState message="No hay preguntas disponibles. Importa el sample desde Dashboard o Documentos." />
      ) : null}
    </div>
  );
}
