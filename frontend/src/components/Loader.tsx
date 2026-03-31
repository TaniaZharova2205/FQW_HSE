export default function Loader({ text = "Загрузка..." }: { text?: string }) {
  return (
    <div className="loader-wrap">
      <div className="loader-spinner" />
      <p>{text}</p>
    </div>
  );
}