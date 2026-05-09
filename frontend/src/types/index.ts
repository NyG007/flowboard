// ============================================================
// FlowBoard — TypeScript Type Definitions
// Tipos espelham exatamente os schemas Pydantic do backend.
// ============================================================

// ── User ─────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  full_name: string;
  username: string;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface UserPublic {
  id: string;
  username: string;
  full_name: string;
  avatar_url: string | null;
}

// ── Auth ─────────────────────────────────────────────────
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  username: string;
  password: string;
}

// ── Board ─────────────────────────────────────────────────
export interface Board {
  id: string;
  title: string;
  description: string | null;
  color: string;
  icon: string | null;
  is_archived: boolean;
  is_public: boolean;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface BoardCreate {
  title: string;
  description?: string;
  color?: string;
  icon?: string;
  is_public?: boolean;
}

// ── Column ────────────────────────────────────────────────
export interface Column {
  id: string;
  title: string;
  color: string;
  position: number;
  wip_limit: number | null;
  board_id: string;
  tasks?: Task[];
}

// ── Task ─────────────────────────────────────────────────
export type TaskPriority = "urgent" | "high" | "medium" | "low" | "no_priority";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  position: number;
  priority: TaskPriority;
  labels: string[];
  cover_color: string | null;
  estimate_hours: number | null;
  is_completed: boolean;
  is_archived: boolean;
  due_date: string | null;
  column_id: string;
  creator_id: string | null;
  assignee_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  labels?: string[];
  due_date?: string;
  assignee_id?: string;
}

// ── Calendar ──────────────────────────────────────────────
export interface CalendarEvent {
  id: string;
  title: string;
  description: string | null;
  color: string;
  start_time: string;
  end_time: string;
  all_day: boolean;
  rrule: string | null;
  task_id: string | null;
  owner_id: string;
}

// ── UI Helpers ────────────────────────────────────────────
export interface ApiError {
  detail: string;
}

export type Theme = "light" | "dark" | "system";

export interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: number;
}
