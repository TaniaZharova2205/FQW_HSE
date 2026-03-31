import { getToken } from "../utils/storage";
import type { ApiError } from "../types";

const API_URL = import.meta.env.VITE_API_URL;

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  auth = false
): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");

  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (auth) {
    const token = getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      //
    }

    const error: ApiError = {
      status: response.status,
      message
    };
    throw error;
  }

  return response.json();
}