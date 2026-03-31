import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import FileUploadForm from "../components/FileUploadForm";
import SpotifyForm from "../components/SpotifyForm";
import TrackHistoryList from "../components/TrackHistoryList";
import Loader from "../components/Loader";
import EmptyState from "../components/EmptyState";
import { getTracks } from "../api/tracks";
import { useToast } from "../context/ToastContext";
import type { Track, TrackCreateResponse, TrackHistoryItem  } from "../types";
import { getTracksHistory } from "../api/tracks";


export default function DashboardPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [tracks, setTracks] = useState<TrackHistoryItem[]>([]);
  const [loadingTracks, setLoadingTracks] = useState(true);

  function handleSuccess(data: TrackCreateResponse) {
    showToast("Задача успешно создана", "success");
    navigate(`/tracks/${data.track_id}?jobId=${data.job_id}`);
  }

  async function loadTracks() {
    try {
      setLoadingTracks(true);
      const data = await getTracksHistory();
      setTracks(data);
    } catch {
      showToast("Не удалось загрузить историю треков", "error");
    } finally {
      setLoadingTracks(false);
    }
  }

  useEffect(() => {
    loadTracks();
  }, []);

  return (
    <Layout>
      <section className="dashboard-hero">
        <span className="page-kicker">Режим тотальной сваги: включен 💅🏻</span>
        <h1 className="page-title">Music Analyzer</h1>
        <p className="page-subtitle">
          Загрузи mp3 или вставь ссылку Spotify — и получи текст трека,
          топ жанров и настроений в стиле настоящих SLAY GIIIIRL.
        </p>
      </section>

      <div className="grid-2">
        <FileUploadForm onSuccess={handleSuccess} />
        <SpotifyForm onSuccess={handleSuccess} />
      </div>

      {loadingTracks ? (
        <Loader text="Загружаем историю анализов..." />
      ) : tracks.length === 0 ? (
        <EmptyState
          title="История пока пустая"
          description="Самое время добавить первый трек и устроить анализ."
        />
      ) : (
        <TrackHistoryList tracks={tracks} />
      )}
    </Layout>
  );
}