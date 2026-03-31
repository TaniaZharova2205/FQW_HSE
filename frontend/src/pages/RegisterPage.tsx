import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      await register(email, password);
      showToast("Регистрация успешна", "success");
      navigate("/", { replace: true });
    } catch (err) {
      const message =
        typeof err === "object" && err && "message" in err
          ? String(err.message)
          : "Ошибка регистрации";
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <div className="auth-card">
        <span className="page-kicker">Создай свою вселенную музыки 💗</span>
        <h1>Регистрация</h1>
        <p className="muted">Создай аккаунт и начни собирать свою историю анализов.</p>
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
            {loading ? "Создаём..." : "Зарегистрироваться"}
          </button>
        </form>

        <p className="muted">
          Уже есть аккаунт? <Link to="/login"><strong>Войти</strong></Link>
        </p>
      </div>
    </Layout>
  );
}