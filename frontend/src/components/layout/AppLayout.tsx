// ============================================================
// FlowBoard — App Layout
// Layout principal com sidebar + conteúdo.
// ============================================================

import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar fixa à esquerda */}
      <Sidebar />

      {/* Conteúdo principal */}
      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="flex-1 overflow-auto"
      >
        {/* Outlet renderiza a página atual (Dashboard, Kanban, etc.) */}
        <Outlet />
      </motion.main>
    </div>
  );
}
