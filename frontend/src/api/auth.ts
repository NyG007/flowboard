// ============================================================
// FlowBoard — Auth API Functions
// ============================================================

import apiClient from "./client";
import type { AuthTokens, LoginRequest, RegisterRequest, User } from "@/types";

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>("/api/v1/auth/login", data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post<User>("/api/v1/auth/register", data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>("/api/v1/auth/me");
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>("/api/v1/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};
