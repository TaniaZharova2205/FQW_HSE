export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface TrackCreateResponse {
  track_id: number;
  job_id: number;
  status: string;
}

export interface Track {
  id: number;
  user_id: number;
  source_type: string;
  spotify_url: string | null;
  original_filename: string | null;
  artist: string | null;
  title: string | null;
  audio_path: string | null;
  created_at: string;
}

export interface Job {
  id: number;
  track_id: number;
  status: string;
  progress: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface PredictionItem {
  label: string;
  score: number;
}

export interface AnalysisResult {
  id: number;
  track_id: number;
  transcription: string | null;

  genre: string | null;
  genre_confidence: number | null;
  top_genres: PredictionItem[] | null;

  mood: string | null;
  mood_confidence: number | null;
  top_moods: PredictionItem[] | null;

  created_at: string;
}

export interface ApiError {
  status?: number;
  message: string;
}

export interface PredictionItem {
  label: string;
  score: number;
}

export interface TrackHistoryItem {
  track_id: number;
  artist: string | null;
  title: string | null;
  source_type: string;
  original_filename: string | null;
  spotify_url: string | null;

  job_id: number | null;
  job_status: string | null;
  job_progress: number | null;
  job_error_message: string | null;

  transcription: string | null;

  genre: string | null;
  genre_confidence: number | null;
  top_genres: PredictionItem[] | null;

  mood: string | null;
  mood_confidence: number | null;
  top_moods: PredictionItem[] | null;

  created_at: string;
}