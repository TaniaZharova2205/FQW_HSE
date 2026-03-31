import { Link } from "react-router-dom";
import Layout from "../components/Layout";

export default function NotFoundPage() {
  return (
    <Layout>
      <div className="card not-found-page">
        <h1>404</h1>
        <p>Страница не найдена</p>
        <Link className="button" to="/">
          На главную
        </Link>
      </div>
    </Layout>
  );
}