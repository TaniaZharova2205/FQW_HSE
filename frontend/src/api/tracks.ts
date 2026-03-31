import { apiRequest } from "./client";
import type { Track, TrackCreateResponse, TrackHistoryItem } from "../types";
import { getToken } from "../utils/storage";

const API_URL = import.meta.env.VITE_API_URL;

export async function uploadTrack(file: File): Promise<TrackCreateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const token = getToken();

  const response = await fetch(`${API_URL}/tracks/upload`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData
  });

  if (!response.ok) {
    let message = "Upload failed";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      //
    }
    throw { status: response.status, message };
  }

  return response.json();
}

export async function createTrackFromSpotify(spotifyUrl: string): Promise<TrackCreateResponse> {
  return apiRequest<TrackCreateResponse>(
    "/tracks/from-spotify",
    {
      method: "POST",
      body: JSON.stringify({ spotify_url: spotifyUrl })
    },
    true
  );
}

export async function getTrack(trackId: number): Promise<Track> {
  return apiRequest<Track>(`/tracks/${trackId}`, { method: "GET" }, true);
}

export async function getTracks(): Promise<Track[]> {
  return apiRequest<Track[]>("/tracks", { method: "GET" }, true);
}

export async function getTracksHistory(): Promise<TrackHistoryItem[]> {
  return apiRequest<TrackHistoryItem[]>("/tracks/history", { method: "GET" }, true);
}