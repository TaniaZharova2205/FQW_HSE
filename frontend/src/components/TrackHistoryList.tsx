import { Link } from "react-router-dom";
import type { PredictionItem, TrackHistoryItem } from "../types";

function PredictionMiniList({
  title,
  items
}: {
  title: string;
  items: PredictionItem[] | null;
}) {
  if (!items || items.length === 0) {
    return (
      <div>
        <strong>{title}:</strong> <span className="muted">нет данных</span>
      </div>
    );
  }

  return (
    <div>
      <strong>{title}:</strong>
      <div className="history-tags">
        {items.map((item, index) => (
          <span key={`${title}-${item.label}-${index}`} className="history-tag">
            {item.label} ({(item.score * 100).toFixed(0)}%)
          </span>
        ))}
      </div>
    </div>
  );
}

function getTrackDisplayTitle(track: TrackHistoryItem): string {
  if (track.artist && track.title) {
    return `${track.artist} — ${track.title}`;
  }

  if (track.source_type === "upload" && track.original_filename) {
    return track.original_filename.replace(/\.[^/.]+$/, "");
  }

  if (track.title) {
    return track.title;
  }

  if (track.artist) {
    return track.artist;
  }

  return "Unknown track";
}

export default function TrackHistoryList({ tracks }: { tracks: TrackHistoryItem[] }) {
  return (
    <div className="card">
      <h3>История анализов</h3>
      <div className="history-list">
        {tracks.map((track) => (
          <div key={track.track_id} className="history-item history-item-full">
            <div className="history-item-top">
              <div>
                <strong>{getTrackDisplayTitle(track)}</strong>
                <p className="muted">
                  {track.source_type === "spotify" ? "Spotify" : "Upload"} · #{track.track_id}
                </p>
              </div>

              <div className="history-actions">
                <span className="badge">
                  {track.job_status || "unknown"}
                </span>
                <Link
                  className="button secondary"
                  to={`/tracks/${track.track_id}?jobId=${track.job_id ?? ""}`}
                >
                  Открыть
                </Link>
                {track.job_status === "done" && (
                  <Link className="button" to={`/results/${track.track_id}`}>
                    Результат
                  </Link>
                )}
              </div>
            </div>

            <div className="divider-soft" />

            <PredictionMiniList title="Топ жанров" items={track.top_genres} />
            <PredictionMiniList title="Топ настроений" items={track.top_moods} />

            <div style={{ marginTop: 12 }}>
              <strong>Текст:</strong>
              <p className="history-transcription">
                {track.transcription
                  ? `${track.transcription.slice(0, 240)}${track.transcription.length > 240 ? "..." : ""}`
                  : "Пока нет текста"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}