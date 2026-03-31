import { Link } from "react-router-dom";
import type { Track } from "../types";

export default function TrackHistoryList({ tracks }: { tracks: Track[] }) {
  return (
    <div className="card">
      <h3>История анализов</h3>
      <div className="history-list">
        {tracks.map((track) => (
          <Link key={track.id} to={`/tracks/${track.id}`} className="history-item">
            <div>
              <strong>{track.artist || "Unknown artist"} — {track.title || "Unknown track"}</strong>
              <p>{track.source_type === "spotify" ? "Spotify" : "Upload"}</p>
            </div>
            <span>#{track.id}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}