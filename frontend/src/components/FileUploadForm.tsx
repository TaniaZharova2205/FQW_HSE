import { useState } from "react";
import { uploadTrack } from "../api/tracks";
import { useToast } from "../context/ToastContext";
import type { TrackCreateResponse } from "../types";

interface Props {
  onSuccess: (data: TrackCreateResponse) => void;
}

export default function FileUploadForm({ onSuccess }: Props) {
  const { showToast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      showToast("Выбери аудиофайл", "error");
      return;
    }

    try {
      setLoading(true);
      const data = await uploadTrack(file);
      showToast("Файл успешно загружен", "success");
      onSuccess(data);
      setFile(null);
    } catch (err) {
      const message =
        typeof err === "object" && err && "message" in err
          ? String(err.message)
          : "Ошибка загрузки";
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="badge">Загрузи свой файл, бэйб 🎧</div>
      <h3 className="form-title">Загрузить аудиофайл</h3>
      <p className="form-subtitle">
        Поддерживаются mp3, wav, ogg, flac, m4a.
      </p>

      <input
        type="file"
        accept=".mp3,.wav,.ogg,.flac,.m4a"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <button className="button" type="submit" disabled={loading}>
        {loading ? "Загрузка..." : "Отправить файл"}
      </button>
    </form>
  );
}