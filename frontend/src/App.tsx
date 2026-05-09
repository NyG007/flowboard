// ============================================================
// FlowBoard — Root Application Component
// ============================================================

import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";

import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { DashboardPage } from "@/pages/DashboardPage";

function App() {
  return (
    <>
      <Toaster position="bottom-right" richColors closeButton duration={4000} />

      <Routes>
        {/* Rotas públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Rotas protegidas — exigem autenticação */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/boards" element={<div className="p-6"><h1 className="text-2xl font-bold">Kanban — Phase 4</h1></div>} />
            <Route path="/calendar" element={<div className="p-6"><h1 className="text-2xl font-bold">Calendário — Phase 5</h1></div>} />
            <Route path="/settings" element={<div className="p-6"><h1 className="text-2xl font-bold">Configurações — Phase 6</h1></div>} />
          </Route>
        </Route>

        {/* Redirect raiz para dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </>
  );
}

export default App;
