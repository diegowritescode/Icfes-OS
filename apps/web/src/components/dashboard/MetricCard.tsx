import { Card, CardTitle } from "@/components/ui/Card";

export function MetricCard({
  title,
  value,
  detail
}: {
  title: string;
  value: string | number;
  detail?: string;
}) {
  return (
    <Card>
      <CardTitle>{title}</CardTitle>
      <div className="mt-3 text-3xl font-semibold text-ink">{value}</div>
      {detail ? <div className="mt-1 text-sm text-slate-500">{detail}</div> : null}
    </Card>
  );
}
