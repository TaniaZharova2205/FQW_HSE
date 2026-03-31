import { apiRequest } from "./client";
import type { AnalysisResult } from "../types";

export async function getResultByTrackId(trackId: number): Promise<AnalysisResult> {
  return apiRequest<AnalysisResult>(`/results/track/${trackId}`, { method: "GET" }, true);
}