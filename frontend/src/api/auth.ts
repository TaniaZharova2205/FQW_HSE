import { apiRequest } from "./client";
import type { TokenResponse, User } from "../types";

export async function register(email: string, password: string): Promise<User> {
  return apiRequest<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export async function getMe(): Promise<User> {
  return apiRequest<User>("/auth/me", { method: "GET" }, true);
}