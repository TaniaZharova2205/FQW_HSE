import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Layout from "../components/Layout";
import ResultCard from "../components/ResultCard";
import Loader from "../components/Loader";
import EmptyState from "../components/EmptyState";
import { getResultByTrackId } from "../api/results";
import { getTrack } from "../api/tracks";
import { useToast } from "../context/ToastContext";
import type { AnalysisResult, ApiError, Track } from "../types";

export default function ResultPage() {
  const { trackId } = useParams();
  const { showToast } = useToast();

  const [track, setTrack] = useState<Track | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!trackId) return;

    async function loadData() {
      try {
        const [trackData, resultData] = await Promise.all([
          getTrack(Number(trackId)),
          getResultByTrackId(Number(trackId))
        ]);
        setTrack(trackData);
        setResult(resultData);
      } catch (err) {
        const error = err as ApiError;
        if (error.status === 404) {
          setNotFound(true);
        } else {
          showToast(error.message || "Ошибка получения результата", "error");
        }
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [trackId]);

  if (loading) {
    return (
      <Layout>
        <Loader text="Загружаем результат..." />
      </Layout>
    );
  }

  if (notFound) {
    return (
      <Layout>
        <EmptyState
          title="Результат пока не готов"
          description="Попробуй вернуться позже или обновить статус задачи."
          action={<Link className="button" to="/">На главную</Link>}
        />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="page-header">
        <h1>Результат анализа</h1>
      </div>

      {track && result ? (
        <ResultCard track={track} result={result} />
      ) : (
        <EmptyState
          title="Нет данных"
          description="Не удалось получить данные анализа."
        />
      )}
    </Layout>
  );
}