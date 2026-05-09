// ============================================================
// FlowBoard — Root Application Component
// Defines the top-level route structure and global providers.
// ============================================================

import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";

// Layouts
// import { AppLayout } from "@/components/layout/AppLayout";
// import { AuthLayout } from "@/components/layout/AuthLayout";

// Pages (will be created in Phase 3)
// import { LoginPage } from "@/pages/auth/LoginPage";
// import { RegisterPage } from "@/pages/auth/RegisterPage";
// import { DashboardPage } from "@/pages/DashboardPage";
// import { KanbanPage } from "@/pages/KanbanPage";
// import { CalendarPage } from "@/pages/CalendarPage";

// Auth guard (will be created in Phase 3)
// import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

function App() {
  return (
    <>
      {/*
        Sonner toast notifications — rendered at root level so any
        component can trigger toasts without prop drilling.
        position="bottom-right" matches Notion, Linear, Vercel UX patterns.
      */}
      <Toaster
        position="bottom-right"
        richColors
        closeButton
        duration={4000}
      />

      <Routes>
        {/* Temporary placeholder — Phase 3 fills these routes */}
        <Route
          path="/"
          element={
            <div className="flex items-center justify-center min-h-screen bg-background">
              <div className="text-center space-y-4">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-8 h-8 bg-brand-600 rounded-lg" />
                  <h1 className="text-3xl font-bold text-foreground">
                    FlowBoard
                  </h1>
                </div>
                <p className="text-muted-foreground">
                  ✅ Phase 1 Complete — Backend & Frontend initialized
                </p>
                <p className="text-sm text-muted-foreground">
                  Phase 2: Backend Foundation coming next...
                </p>
              </div>
            </div>
          }
        />
      </Routes>
    </>
  );
}

export default App;