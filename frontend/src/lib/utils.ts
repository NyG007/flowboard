// ============================================================
// FlowBoard — Utility Functions
// ============================================================

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combina classes Tailwind de forma inteligente.
 * twMerge resolve conflitos (ex: "p-2 p-4" → "p-4")
 * clsx lida com condicionais (ex: { "bg-red": isError })
 *
 * Uso: cn("base-class", isActive && "active-class", className)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formata data para exibição amigável.
 */
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

/**
 * Retorna as iniciais do nome completo.
 * "João Silva" → "JS"
 */
export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

/**
 * Cores de prioridade para badges e ícones.
 */
export const PRIORITY_CONFIG = {
  urgent: { label: "Urgente", color: "text-red-500", bg: "bg-red-500/10" },
  high: { label: "Alta", color: "text-orange-500", bg: "bg-orange-500/10" },
  medium: { label: "Média", color: "text-yellow-500", bg: "bg-yellow-500/10" },
  low: { label: "Baixa", color: "text-blue-500", bg: "bg-blue-500/10" },
  no_priority: { label: "Sem prioridade", color: "text-muted-foreground", bg: "bg-muted" },
} as const;

/**
 * Trunca texto longo com reticências.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + "...";
}
