// ============================================================
// FlowBoard — Protected Route
// Redireciona para /login se não estiver autenticado.
// ============================================================

import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (!isAuthenticated) {
    // Redireciona para login preservando a URL tentada
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
