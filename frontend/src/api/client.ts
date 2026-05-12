import { getToken } from "../utils/storage";
import type { ApiError } from "../types";

const API_URL = import.meta.env.VITE_API_URL;

function getErrorMessage(data: unknown): string {
  if (
    typeof data === "object" &&
    data !== null &&
    "detail" in data
  ) {
    const detail = (data as { detail: unknown }).detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item
          ) {
            return String((item as { msg: unknown }).msg).replace(/^Value error,\s*/i, "");
          }

          return String(item);
        })
        .join("\n");
    }
  }

  return "Ошибка запроса";
}

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
    let message = "Ошибка запроса";

    try {
      const data = await response.json();
      message = getErrorMessage(data);
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