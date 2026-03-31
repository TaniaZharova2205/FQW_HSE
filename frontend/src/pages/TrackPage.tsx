import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import Layout from "../components/Layout";
import JobStatusCard from "../components/JobStatusCard";
import Loader from "../components/Loader";
import EmptyState from "../components/EmptyState";
import { getTrack } from "../api/tracks";
import { getJob } from "../api/jobs";
import { useToast } from "../context/ToastContext";
import type { Job, Track, ApiError } from "../types";

export default function TrackPage() {
  const { trackId } = useParams();
  const [searchParams] = useSearchParams();
  const jobId = searchParams.get("jobId");

  const { showToast } = useToast();

  const [track, setTrack] = useState<Track | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshingJob, setRefreshingJob] = useState(false);
  const [notFound, setNotFound] = useState(false);

  async function loadTrack() {
    if (!trackId) return;

    try {
      const data = await getTrack(Number(trackId));
      setTrack(data);
      setNotFound(false);
    } catch (err) {
      const error = err as ApiError;
      if (error.status === 404) {
        setNotFound(true);
      } else {
        showToast(error.message || "Ошибка получения трека", "error");
      }
    }
  }

  async function loadJob(showLoader = false) {
    if (!jobId) return;

    try {
      if (showLoader) {
        setRefreshingJob(true);
      }
      const data = await getJob(Number(jobId));
      setJob(data);
    } catch (err) {
      const error = err as ApiError;
      showToast(error.message || "Ошибка получения job", "error");
    } finally {
      if (showLoader) {
        setRefreshingJob(false);
      }
    }
  }

  useEffect(() => {
    async function init() {
      setLoading(true);
      await loadTrack();
      await loadJob();
      setLoading(false);
    }

    init();
  }, [trackId, jobId]);

  useEffect(() => {
    if (!jobId || !job) return;
    if (job.status === "done" || job.status === "failed") return;

    const intervalId = window.setInterval(() => {
      loadJob();
    }, 3000);

    return () => clearInterval(intervalId);
  }, [jobId, job?.status]);

  if (loading) {
    return (
      <Layout>
        <Loader text="Загружаем трек..." />
      </Layout>
    );
  }

  if (notFound) {
    return (
      <Layout>
        <EmptyState
          title="Трек не найден"
          description="Возможно, он был удалён или у тебя нет к нему доступа."
          action={<Link className="button" to="/">Вернуться на главную</Link>}
        />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="page-header">
        <h1>Трек</h1>
      </div>

      {track && (
        <div className="card">
          <p><strong>ID:</strong> {track.id}</p>
          <p><strong>Источник:</strong> {track.source_type}</p>
          <p><strong>Artist:</strong> {track.artist || "—"}</p>
          <p><strong>Title:</strong> {track.title || "—"}</p>
          <p><strong>Original filename:</strong> {track.original_filename || "—"}</p>
        </div>
      )}

      {job ? (
        <JobStatusCard
          job={job}
          onRefresh={() => loadJob(true)}
          refreshing={refreshingJob}
        />
      ) : (
        <EmptyState
          title="Информация о задаче недоступна"
          description="Job ID не передан или задача ещё не найдена."
        />
      )}

      {job?.status === "done" && track && (
        <Link className="button" to={`/results/${track.id}`}>
          Посмотреть результат
        </Link>
      )}
    </Layout>
  );
}