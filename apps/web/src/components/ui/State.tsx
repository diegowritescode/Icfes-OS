import { AlertCircle, Loader2 } from "lucide-react";

export function LoadingState({ label = "Cargando" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 rounded border border-line bg-white p-4 text-sm text-slate-600">
      <Loader2 className="animate-spin" size={18} />
      {label}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 rounded border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
      <AlertCircle size={18} />
      {message}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return <div className="rounded border border-dashed border-line bg-white p-6 text-sm text-slate-500">{message}</div>;
}
