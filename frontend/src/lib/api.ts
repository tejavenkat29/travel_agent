import type { ApiError, FinalResponse } from "./types";

// Same-origin in dev via the Vite proxy (`/api` -> backend). In production,
// set VITE_API_BASE to the backend URL (and configure CORS there).
const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function planTrip(
  request: string,
  includeWeather = true,
): Promise<FinalResponse> {
  const res = await fetch(`${API_BASE}/api/v1/plan`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ request, include_weather: includeWeather }),
  });

  const data: unknown = await res.json().catch(() => null);

  if (!res.ok || (data as ApiError)?.error) {
    const message =
      (data as ApiError)?.message ?? `Request failed (${res.status}).`;
    throw new Error(message);
  }
  return data as FinalResponse;
}
