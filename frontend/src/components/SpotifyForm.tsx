import { useState } from "react";
import { createTrackFromSpotify } from "../api/tracks";
import { useToast } from "../context/ToastContext";
import type { TrackCreateResponse } from "../types";

interface Props {
  onSuccess: (data: TrackCreateResponse) => void;
}

export default function SpotifyForm({ onSuccess }: Props) {
  const { showToast } = useToast();
  const [spotifyUrl, setSpotifyUrl] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    try {
      setLoading(true);
      const data = await createTrackFromSpotify(spotifyUrl);
      showToast("Spotify-ссылка отправлена", "success");
      onSuccess(data);
      setSpotifyUrl("");
    } catch (err) {
      const message =
        typeof err === "object" && err && "message" in err
          ? String(err.message)
          : "Ошибка отправки ссылки";
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="badge">Режим богини spotify 💋</div>
      <h3 className="form-title">Ссылка Spotify</h3>
      <p className="form-subtitle">
        Вставь ссылку на трек, а дальше система сама всё сделает.
      </p>

      <input
        type="text"
        placeholder="https://open.spotify.com/track/..."
        value={spotifyUrl}
        onChange={(e) => setSpotifyUrl(e.target.value)}
      />

      <button className="button" type="submit" disabled={loading}>
        {loading ? "Отправка..." : "Отправить ссылку"}
      </button>
    </form>
  );
}