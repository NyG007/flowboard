import apiClient from "./client";
import type { Board, BoardCreate, Column, Task, TaskCreate } from "@/types";

export const boardsApi = {
  list: async (): Promise<Board[]> => {
    const { data } = await apiClient.get("/api/v1/boards");
    return data;
  },
  create: async (payload: BoardCreate): Promise<Board> => {
    const { data } = await apiClient.post("/api/v1/boards", payload);
    return data;
  },
  get: async (id: string): Promise<Board> => {
    const { data } = await apiClient.get(`/api/v1/boards/${id}`);
    return data;
  },
  update: async (id: string, payload: Partial<BoardCreate>): Promise<Board> => {
    const { data } = await apiClient.patch(`/api/v1/boards/${id}`, payload);
    return data;
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/boards/${id}`);
  },

  // Columns
  getColumns: async (boardId: string): Promise<Column[]> => {
    const { data } = await apiClient.get(`/api/v1/boards/${boardId}/columns`);
    return data;
  },
  createColumn: async (boardId: string, payload: { title: string; color?: string; position?: number }): Promise<Column> => {
    const { data } = await apiClient.post(`/api/v1/boards/${boardId}/columns`, payload);
    return data;
  },
  updateColumn: async (boardId: string, columnId: string, payload: Partial<Column>): Promise<Column> => {
    const { data } = await apiClient.patch(`/api/v1/boards/${boardId}/columns/${columnId}`, payload);
    return data;
  },
  deleteColumn: async (boardId: string, columnId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/boards/${boardId}/columns/${columnId}`);
  },

  // Tasks
  getTasks: async (boardId: string, columnId: string): Promise<Task[]> => {
    const { data } = await apiClient.get(`/api/v1/boards/${boardId}/columns/${columnId}/tasks`);
    return data;
  },
  createTask: async (boardId: string, columnId: string, payload: TaskCreate): Promise<Task> => {
    const { data } = await apiClient.post(`/api/v1/boards/${boardId}/columns/${columnId}/tasks`, payload);
    return data;
  },
  updateTask: async (boardId: string, taskId: string, payload: Partial<Task>): Promise<Task> => {
    const { data } = await apiClient.patch(`/api/v1/boards/${boardId}/tasks/${taskId}`, payload);
    return data;
  },
  deleteTask: async (boardId: string, taskId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/boards/${boardId}/tasks/${taskId}`);
  },
};