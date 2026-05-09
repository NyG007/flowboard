// ============================================================
// FlowBoard — React Application Bootstrap
// This is the entry point that mounts the React tree to the DOM.
// ============================================================

import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

/**
 * TanStack Query Client Configuration
 * These settings are tuned for a real-time productivity app:
 * - staleTime: Data is "fresh" for 1 min — reduces unnecessary refetches
 * - retry: Only retry once on failure (don't hammer a failing API)
 * - refetchOnWindowFocus: Re-sync data when user switches back to tab
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,        // 1 minute
      retry: 1,
      refetchOnWindowFocus: true,
    },
    mutations: {
      retry: 0,                    // Don't retry mutations (e.g., don't double-submit forms)
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {/* QueryClientProvider: makes queryClient available throughout the entire app */}
    <QueryClientProvider client={queryClient}>
      {/* BrowserRouter: enables HTML5 history API routing */}
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);