import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function LoginPage() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      await login(email, password);
      showToast("Успешный вход", "success");
      navigate("/", { replace: true });
    } catch (err) {
      const message =
        typeof err === "object" && err && "message" in err
          ? String(err.message)
          : "Ошибка входа";
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <div className="auth-card">
        <span className="page-kicker">Добро пожаловать назад, мой падший ангел ✨</span>
        <h1>Вход</h1>
        <p className="muted">Войди в аккаунт и продолжай анализировать музыку.</p>
        <div className="divider-soft" />

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className="button" type="submit" disabled={loading}>
            {loading ? "Входим..." : "Войти"}
          </button>
        </form>

        <p className="muted">
          Нет аккаунта? <Link to="/register"><strong>Зарегистрироваться</strong></Link>
        </p>
      </div>
    </Layout>
  );
}