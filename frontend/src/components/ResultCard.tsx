import type { AnalysisResult, PredictionItem, Track } from "../types";

interface Props {
  track: Track;
  result: AnalysisResult;
}

function PredictionList({
  title,
  items
}: {
  title: string;
  items: PredictionItem[] | null;
}) {
  return (
    <div className="prediction-block">
      <h3>{title}</h3>
      {!items || items.length === 0 ? (
        <p className="muted">Нет данных</p>
      ) : (
        <div className="prediction-list">
          {items.map((item, index) => (
            <div key={`${title}-${item.label}-${index}`} className="prediction-item">
              <span>
                {index + 1}. {item.label}
              </span>
              <strong>{(item.score * 100).toFixed(2)}%</strong>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ResultCard({ track, result }: Props) {
  return (
    <div className="card">
      <span className="page-kicker">analysis complete 💞</span>
      <h2>
        {track.artist || "Unknown artist"} — {track.title || "Unknown track"}
      </h2>

      <p className="muted"><strong>Источник:</strong> {track.source_type}</p>

      <div className="grid-2">
        <PredictionList title="Топ-3 жанра" items={result.top_genres} />
        <PredictionList title="Топ-3 настроения" items={result.top_moods} />
      </div>

      <div style={{ marginTop: 20 }}>
        <strong>Текст:</strong>
        <pre className="lyrics-block">{result.transcription || "Пока нет текста"}</pre>
      </div>
    </div>
  );
}