import type { Job } from "../types";

interface Props {
  job: Job;
  onRefresh?: () => void;
  refreshing?: boolean;
}

export default function JobStatusCard({ job, onRefresh, refreshing = false }: Props) {
  return (
    <div className="card">
      <div className="card-header-row">
        <h3>Статус задачи</h3>
        {onRefresh && (
          <button className="button secondary" onClick={onRefresh} disabled={refreshing}>
            {refreshing ? "Обновляем..." : "Обновить статус"}
          </button>
        )}
      </div>

      <p><strong>ID job:</strong> {job.id}</p>
      <p><strong>Track ID:</strong> {job.track_id}</p>
      <p><strong>Статус:</strong> {job.status}</p>
      <p><strong>Прогресс:</strong> {job.progress}%</p>

      <div className="progress-bar">
        <div className="progress-bar-fill" style={{ width: `${job.progress}%` }} />
      </div>

      {job.error_message && <p className="error">{job.error_message}</p>}
    </div>
  );
}