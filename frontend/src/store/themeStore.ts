// ============================================================
// FlowBoard — Theme Store (Zustand)
// Gerencia dark/light mode com persistência.
// ============================================================

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Theme } from "@/types";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: "dark" as Theme,

      setTheme: (theme) => {
        applyTheme(theme);
        set({ theme });
      },

      toggleTheme: () => {
        const current = get().theme;
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        set({ theme: next });
      },
    }),
    {
      name: "flowboard-theme",
      onRehydrateStorage: () => (state) => {
        // Aplicar o tema salvo ao carregar a página
        if (state) applyTheme(state.theme);
      },
    }
  )
);

/**
 * Aplica o tema no elemento <html>.
 * Tailwind usa a classe 'dark' no elemento raiz para ativar dark mode.
 */
function applyTheme(theme: Theme) {
  const root = document.documentElement;
  const isDark =
    theme === "dark" ||
    (theme === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  root.classList.toggle("dark", isDark);
}
