import { apiRequest } from "./client";
import type { Job } from "../types";

export async function getJob(jobId: number): Promise<Job> {
  return apiRequest<Job>(`/jobs/${jobId}`, { method: "GET" }, true);
}