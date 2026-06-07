const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {})
      },
      cache: "no-store"
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "network error";
    throw new Error(`No se pudo conectar con la API en ${API_URL}. Detalle: ${message}`);
  }

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // Keep default message.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function uploadFile<T>(path: string, file: File): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      body: form
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "network error";
    throw new Error(`No se pudo conectar con la API en ${API_URL}. Detalle: ${message}`);
  }
  if (!response.ok) {
    throw new Error(`Upload failed with HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}
