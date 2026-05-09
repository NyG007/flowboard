// ============================================================
// FlowBoard — Vite Configuration
// ============================================================

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [
    react(), // Enables React Fast Refresh for instant HMR
  ],

  resolve: {
    alias: {
      // '@/components/...' instead of '../../components/...'
      // This is the single most important DX improvement for large projects
      "@": path.resolve(__dirname, "./src"),
    },
  },

  server: {
    host: "0.0.0.0",    // Bind to all interfaces (required inside Docker)
    port: 5173,
    proxy: {
      // All requests starting with /api are proxied to FastAPI
      // This eliminates CORS issues during development
      "/api": {
        target: "http://backend:8000",   // 'backend' = Docker service name
        changeOrigin: true,
        secure: false,
      },
      // WebSocket proxy for real-time features
      "/ws": {
        target: "ws://backend:8000",
        ws: true,                        // Enable WebSocket proxying
        changeOrigin: true,
      },
    },
  },

  build: {
    // Split vendor chunks for better browser caching
    // React, FullCalendar, dnd-kit each get their own chunk
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom", "react-router-dom"],
          dnd: ["@dnd-kit/core", "@dnd-kit/sortable"],
          calendar: [
            "@fullcalendar/react",
            "@fullcalendar/daygrid",
            "@fullcalendar/timegrid",
          ],
          ui: ["framer-motion", "lucide-react"],
        },
      },
    },
    sourcemap: true,       // Enable in development for debugging
    minify: "esbuild",     // Fastest minification (10x faster than Terser)
  },
});