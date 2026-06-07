export function Field({
  label,
  children
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="grid gap-1 text-sm">
      <span className="font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

export const inputClass =
  "focus-ring min-h-10 rounded border border-line bg-white px-3 py-2 text-sm text-ink";
