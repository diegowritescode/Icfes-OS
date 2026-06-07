"use client";

import { useEffect, useState } from "react";
import { FileUp, RefreshCw } from "lucide-react";
import { apiFetch, uploadFile } from "@/lib/api";
import type { DocumentSource } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/State";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSource[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

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

  async function importSample() {
    await apiFetch("/documents/import-sample", { method: "POST" });
    await load();
  }

  async function importFile(file: File | null) {
    if (!file) return;
    const lower = file.name.toLowerCase();
    if (lower.endsWith(".jsonl")) await uploadFile("/documents/import-jsonl", file);
    else if (lower.endsWith(".csv")) await uploadFile("/documents/import-csv", file);
    else if (lower.endsWith(".pdf")) await uploadFile("/documents/extract-pdf", file);
    else throw new Error("Formato no soportado");
    await load();
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

      <Card>
        <CardTitle>Fuentes importadas</CardTitle>
        <div className="mt-4">
          {documents.length ? (
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  <th className="py-2 pr-3">Archivo</th>
                  <th className="py-2 pr-3">Tipo</th>
                  <th className="py-2 pr-3">Area</th>
                  <th className="py-2 pr-3">Importado</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((item) => (
                  <tr key={item.id} className="border-t border-line">
                    <td className="py-2 pr-3 font-medium">{item.filename}</td>
                    <td className="py-2 pr-3">
                      <Badge>{item.source_type}</Badge>
                    </td>
                    <td className="py-2 pr-3">{item.area ?? "mixto"}</td>
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
    </div>
  );
}
