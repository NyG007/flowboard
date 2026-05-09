// ============================================================
// FlowBoard — Sidebar Component
// Sidebar animada com Framer Motion, colapsável.
// ============================================================

import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Kanban,
  Calendar,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Moon,
  Sun,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/uiStore";
import { useAuthStore } from "@/store/authStore";
import { useThemeStore } from "@/store/themeStore";
import { getInitials } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Kanban", href: "/boards", icon: Kanban },
  { label: "Calendário", href: "/calendar", icon: Calendar },
  { label: "Configurações", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();

  return (
    <motion.aside
      animate={{ width: sidebarCollapsed ? 64 : 240 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="relative flex flex-col h-full bg-[hsl(var(--sidebar-bg))] border-r border-[hsl(var(--sidebar-border))] overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-[hsl(var(--sidebar-border))]">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
          <LayoutDashboard className="w-4 h-4 text-primary-foreground" />
        </div>
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
              className="ml-3 font-bold text-white text-lg"
            >
              FlowBoard
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "flex items-center gap-3 px-2 py-2.5 rounded-lg transition-colors group",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-slate-400 hover:bg-[hsl(var(--sidebar-accent))] hover:text-white"
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-sm font-medium"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          );
        })}
      </nav>

      {/* Bottom — User + Actions */}
      <div className="p-2 border-t border-[hsl(var(--sidebar-border))] space-y-1">
        {/* Toggle theme */}
        <button
          onClick={toggleTheme}
          className="flex items-center gap-3 w-full px-2 py-2.5 rounded-lg text-slate-400 hover:bg-[hsl(var(--sidebar-accent))] hover:text-white transition-colors"
        >
          {theme === "dark" ? (
            <Sun className="w-5 h-5 flex-shrink-0" />
          ) : (
            <Moon className="w-5 h-5 flex-shrink-0" />
          )}
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-sm"
              >
                {theme === "dark" ? "Modo claro" : "Modo escuro"}
              </motion.span>
            )}
          </AnimatePresence>
        </button>

        {/* User info */}
        {user && (
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-primary-foreground">
                {getInitials(user.full_name)}
              </span>
            </div>
            <AnimatePresence>
              {!sidebarCollapsed && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 min-w-0"
                >
                  <p className="text-sm font-medium text-white truncate">
                    {user.full_name}
                  </p>
                  <p className="text-xs text-slate-400 truncate">
                    @{user.username}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Logout */}
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-2 py-2.5 rounded-lg text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-colors"
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-sm"
              >
                Sair
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>

      {/* Toggle button */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-20 w-6 h-6 bg-border rounded-full flex items-center justify-center hover:bg-primary transition-colors z-10 border border-border"
      >
        {sidebarCollapsed ? (
          <ChevronRight className="w-3 h-3 text-foreground" />
        ) : (
          <ChevronLeft className="w-3 h-3 text-foreground" />
        )}
      </button>
    </motion.aside>
  );
}
