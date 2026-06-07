"use client";

import { useEffect, useState } from "react";
import { Check, FileUp, RefreshCw, X } from "lucide-react";
import { apiFetch, uploadFile } from "@/lib/api";
import type {
  DocumentDetail,
  DocumentSource,
  ImportSummary,
  PdfExtractSummary,
  Question,
  QuestionCandidate
} from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Field, inputClass } from "@/components/ui/Field";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/State";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSource[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<DocumentDetail | null>(null);
  const [editing, setEditing] = useState<QuestionCandidate | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setDocuments(await apiFetch<DocumentSource[]>("/documents"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando documentos");
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(documentId: number) {
    setSelectedId(documentId);
    setDetailLoading(true);
    setError(null);
    try {
      const data = await apiFetch<DocumentDetail>(`/documents/${documentId}`);
      setDetail(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando documento");
    } finally {
      setDetailLoading(false);
    }
  }

  async function importSample() {
    const result = await apiFetch<ImportSummary>("/documents/import-sample", { method: "POST" });
    setSummary(`Sample: ${result.imported_count} importadas, ${result.skipped_count} omitidas.`);
    await load();
    await loadDetail(result.document.id);
  }

  async function importFile(file: File | null) {
    if (!file) return;
    const lower = file.name.toLowerCase();
    if (lower.endsWith(".jsonl")) {
      const result = await uploadFile<ImportSummary>("/documents/import-jsonl", file);
      setSummary(
        `${file.name}: ${result.imported_count} importadas, ${result.skipped_count} omitidas, ${result.errors.length} errores.`
      );
      await load();
      await loadDetail(result.document.id);
    } else if (lower.endsWith(".csv")) {
      const result = await uploadFile<ImportSummary>("/documents/import-csv", file);
      setSummary(
        `${file.name}: ${result.imported_count} importadas, ${result.skipped_count} omitidas, ${result.errors.length} errores.`
      );
      await load();
      await loadDetail(result.document.id);
    } else if (lower.endsWith(".pdf")) {
      const result = await uploadFile<PdfExtractSummary>("/documents/extract-pdf", file);
      setSummary(`${file.name}: ${result.pages} paginas extraidas, ${result.candidate_count} candidatos.`);
      await load();
      await loadDetail(result.document_id);
    } else {
      throw new Error("Formato no soportado");
    }
  }

  async function saveCandidate(candidate: QuestionCandidate) {
    const updated = await apiFetch<QuestionCandidate>(`/documents/candidates/${candidate.id}`, {
      method: "PATCH",
      body: JSON.stringify(candidate)
    });
    setEditing(updated);
    if (selectedId) await loadDetail(selectedId);
  }

  async function approveCandidate(candidate: QuestionCandidate) {
    const question = await apiFetch<Question>(`/documents/candidates/${candidate.id}/approve`, {
      method: "POST"
    });
    setSummary(`Candidato ${candidate.id} aprobado como pregunta ${question.id}.`);
    setEditing(null);
    if (selectedId) await loadDetail(selectedId);
  }

  async function rejectCandidate(candidate: QuestionCandidate) {
    const updated = await apiFetch<QuestionCandidate>(`/documents/candidates/${candidate.id}/reject`, {
      method: "POST"
    });
    setSummary(`Candidato ${updated.id} rechazado.`);
    setEditing(null);
    if (selectedId) await loadDetail(selectedId);
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Documentos</h1>
        <p className="mt-1 text-sm text-slate-600">Importa JSONL/CSV o extrae texto basico de PDFs para revision.</p>
      </div>

      <Card>
        <div className="flex flex-wrap gap-3">
          <Button onClick={importSample}>
            <FileUp size={16} />
            Importar sample
          </Button>
          <label className="focus-ring inline-flex min-h-10 cursor-pointer items-center justify-center rounded border border-line bg-white px-3 text-sm font-medium hover:bg-panel">
            Subir archivo
            <input
              className="hidden"
              type="file"
              accept=".jsonl,.csv,.pdf"
              onChange={(event) => {
                void importFile(event.target.files?.[0] ?? null).catch((err) => setError(err.message));
              }}
            />
          </label>
          <Button variant="secondary" onClick={load}>
            <RefreshCw size={16} />
          </Button>
        </div>
      </Card>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {summary ? <div className="rounded border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900">{summary}</div> : null}

      <div className="grid gap-4 xl:grid-cols-[0.85fr_1.15fr]">
        <Card>
          <CardTitle>Fuentes importadas</CardTitle>
          <div className="mt-4">
            {documents.length ? (
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-2 pr-3">Archivo</th>
                    <th className="py-2 pr-3">Tipo</th>
                    <th className="py-2 pr-3">Estado</th>
                    <th className="py-2 pr-3">Importado</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((item) => (
                    <tr
                      key={item.id}
                      className="cursor-pointer border-t border-line hover:bg-panel"
                      onClick={() => void loadDetail(item.id)}
                    >
                      <td className="py-2 pr-3 font-medium">{item.filename}</td>
                      <td className="py-2 pr-3">
                        <Badge>{item.source_type}</Badge>
                      </td>
                      <td className="py-2 pr-3">{String(item.metadata_json.status ?? "imported")}</td>
                      <td className="py-2 pr-3">{new Date(item.imported_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState message="No hay documentos importados. Usa el sample para activar la app en segundos." />
            )}
          </div>
        </Card>

        <Card>
          <CardTitle>Vista de documento</CardTitle>
          {detailLoading ? <div className="mt-4"><LoadingState label="Cargando documento" /></div> : null}
          {!detail && !detailLoading ? (
            <div className="mt-4">
              <EmptyState message="Selecciona un documento para ver paginas extraidas y candidatos." />
            </div>
          ) : null}
          {detail ? (
            <div className="mt-4 space-y-5">
              <div className="flex flex-wrap items-center gap-2">
                <Badge>{detail.source_type}</Badge>
                <Badge>{detail.pages.length} paginas</Badge>
                <Badge>{detail.candidates.length} candidatos</Badge>
              </div>
              <div>
                <h2 className="font-medium">{detail.filename}</h2>
                <p className="mt-1 text-sm text-slate-500">{new Date(detail.imported_at).toLocaleString()}</p>
              </div>

              <section>
                <h3 className="text-sm font-semibold uppercase text-slate-500">Candidatos</h3>
                <div className="mt-3 space-y-3">
                  {detail.candidates.length ? (
                    detail.candidates.map((candidate) => (
                      <CandidateRow
                        key={candidate.id}
                        candidate={candidate}
                        editing={editing}
                        setEditing={setEditing}
                        onSave={saveCandidate}
                        onApprove={approveCandidate}
                        onReject={rejectCandidate}
                      />
                    ))
                  ) : (
                    <EmptyState message="Este documento no tiene candidatos. Revisa el texto extraido y crea un JSONL/CSV corregido si hace falta." />
                  )}
                </div>
              </section>

              <section>
                <h3 className="text-sm font-semibold uppercase text-slate-500">Texto extraido</h3>
                <div className="mt-3 max-h-[520px] space-y-3 overflow-auto">
                  {detail.pages.length ? (
                    detail.pages.map((page) => (
                      <details key={page.id} className="rounded border border-line bg-panel p-3">
                        <summary className="cursor-pointer text-sm font-medium">Pagina {page.page}</summary>
                        <pre className="mt-3 whitespace-pre-wrap text-xs leading-5 text-slate-700">{page.text}</pre>
                      </details>
                    ))
                  ) : (
                    <EmptyState message="Este documento no tiene texto extraido guardado." />
                  )}
                </div>
              </section>
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}

function CandidateRow({
  candidate,
  editing,
  setEditing,
  onSave,
  onApprove,
  onReject
}: {
  candidate: QuestionCandidate;
  editing: QuestionCandidate | null;
  setEditing: (candidate: QuestionCandidate | null) => void;
  onSave: (candidate: QuestionCandidate) => Promise<void>;
  onApprove: (candidate: QuestionCandidate) => Promise<void>;
  onReject: (candidate: QuestionCandidate) => Promise<void>;
}) {
  const current = editing?.id === candidate.id ? editing : candidate;
  const isEditing = editing?.id === candidate.id;

  function update<K extends keyof QuestionCandidate>(key: K, value: QuestionCandidate[K]) {
    setEditing({ ...current, [key]: value });
  }

  return (
    <div className="rounded border border-line p-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="font-medium">Candidato {candidate.id}</div>
          <div className="mt-1 text-xs text-slate-500">Pagina {candidate.page ?? "n/a"}</div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge>{candidate.status}</Badge>
          <Button variant="secondary" onClick={() => setEditing(isEditing ? null : candidate)}>
            Editar
          </Button>
          <Button
            variant="secondary"
            disabled={candidate.status === "approved"}
            onClick={() => void onApprove(current)}
          >
            <Check size={16} />
          </Button>
          <Button
            variant="danger"
            disabled={candidate.status === "rejected"}
            onClick={() => void onReject(candidate)}
          >
            <X size={16} />
          </Button>
        </div>
      </div>

      {isEditing ? (
        <div className="mt-4 grid gap-3">
          <Field label="Area">
            <select
              className={inputClass}
              value={current.area ?? ""}
              onChange={(event) => update("area", event.target.value as QuestionCandidate["area"])}
            >
              <option value="">Seleccionar</option>
              <option value="ciencias_naturales">Ciencias</option>
              <option value="matematicas">Matematicas</option>
              <option value="sociales_ciudadanas">Sociales</option>
              <option value="lectura_critica">Lectura</option>
              <option value="ingles">Ingles</option>
            </select>
          </Field>
          <div className="grid gap-3 md:grid-cols-3">
            <Field label="Ano">
              <input
                className={inputClass}
                type="number"
                value={current.year ?? ""}
                onChange={(event) => update("year", event.target.value ? Number(event.target.value) : null)}
              />
            </Field>
            <Field label="Subarea">
              <input className={inputClass} value={current.subarea ?? ""} onChange={(event) => update("subarea", event.target.value)} />
            </Field>
            <Field label="Tema">
              <input className={inputClass} value={current.topic ?? ""} onChange={(event) => update("topic", event.target.value)} />
            </Field>
          </div>
          <Field label="Enunciado">
            <textarea className={`${inputClass} min-h-28`} value={current.statement ?? ""} onChange={(event) => update("statement", event.target.value)} />
          </Field>
          <div className="grid gap-3 md:grid-cols-2">
            {(["A", "B", "C", "D"] as const).map((letter) => {
              const key = `option_${letter.toLowerCase()}` as keyof QuestionCandidate;
              return (
                <Field key={letter} label={`Opcion ${letter}`}>
                  <textarea className={`${inputClass} min-h-20`} value={String(current[key] ?? "")} onChange={(event) => update(key, event.target.value as never)} />
                </Field>
              );
            })}
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <Field label="Correcta">
              <select
                className={inputClass}
                value={current.correct_answer ?? ""}
                onChange={(event) => update("correct_answer", event.target.value as QuestionCandidate["correct_answer"])}
              >
                <option value="">Sin clave</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
            </Field>
            <Field label="Subtema">
              <input className={inputClass} value={current.subtopic ?? ""} onChange={(event) => update("subtopic", event.target.value)} />
            </Field>
          </div>
          <Field label="Explicacion">
            <textarea className={`${inputClass} min-h-20`} value={current.explanation ?? ""} onChange={(event) => update("explanation", event.target.value)} />
          </Field>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => void onSave(current)}>Guardar candidato</Button>
            <Button variant="secondary" onClick={() => setEditing(null)}>Cancelar</Button>
          </div>
        </div>
      ) : (
        <div className="mt-3 text-sm leading-6 text-slate-700">
          <p className="line-clamp-3">{candidate.statement || candidate.raw_text}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge>{candidate.area ?? "sin_area"}</Badge>
            <Badge>{candidate.topic ?? "sin_tema"}</Badge>
            <Badge>{candidate.correct_answer ?? "sin_clave"}</Badge>
          </div>
        </div>
      )}
    </div>
  );
}
