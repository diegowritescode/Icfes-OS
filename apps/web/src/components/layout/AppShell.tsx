"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BookOpenCheck,
  CalendarDays,
  Database,
  FileText,
  Gauge,
  Settings,
  Target
} from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { href: "/", label: "Dashboard", icon: Gauge },
  { href: "/documents", label: "Documentos", icon: FileText },
  { href: "/questions", label: "Preguntas", icon: Database },
  { href: "/practice", label: "Practica", icon: BookOpenCheck },
  { href: "/study-plan", label: "Plan diario", icon: CalendarDays },
  { href: "/analytics", label: "Analitica", icon: BarChart3 },
  { href: "/settings", label: "Config", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen lg:flex">
      <aside className="border-line bg-ink text-white lg:fixed lg:inset-y-0 lg:w-64">
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-3 border-b border-white/10 px-5 py-5">
            <div className="flex size-10 items-center justify-center rounded bg-emerald-500 text-ink">
              <Target size={22} />
            </div>
            <div>
              <div className="text-base font-semibold">ICFES OS</div>
              <div className="text-xs text-white/60">Saber 11 intelligence</div>
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-3 py-3 lg:flex-col lg:overflow-visible">
            {items.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex min-w-fit items-center gap-3 rounded px-3 py-2 text-sm text-white/75 transition hover:bg-white/10 hover:text-white",
                    active && "bg-white text-ink hover:bg-white hover:text-ink"
                  )}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="mt-auto hidden border-t border-white/10 p-4 text-xs leading-5 text-white/55 lg:block">
            Prioridad actual: Ciencias, Matematicas y Sociales. Lectura e Ingles quedan en mantenimiento.
          </div>
        </div>
      </aside>
      <main className="w-full lg:pl-64">
        <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}
