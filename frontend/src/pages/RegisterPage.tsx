import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

function validateEmail(email: string): string | null {
  if (!email.trim()) {
    return "Введите email";
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return "Введите корректный email";
  }

  return null;
}

function validatePassword(password: string): string | null {
  if (!password) {
    return "Введите пароль";
  }

  if (password.length < 8) {
    return "Пароль должен содержать минимум 8 символов";
  }

  if (!/[a-z]/.test(password)) {
    return "Пароль должен содержать хотя бы одну строчную букву";
  }

  if (!/[A-Z]/.test(password)) {
    return "Пароль должен содержать хотя бы одну заглавную букву";
  }

  if (!/\d/.test(password)) {
    return "Пароль должен содержать хотя бы одну цифру";
  }

  if (!/[^\w\s]/.test(password)) {
    return "Пароль должен содержать хотя бы один специальный символ";
  }

  return null;
}

export default function RegisterPage() {
  const { register } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [emailTouched, setEmailTouched] = useState(false);
  const [passwordTouched, setPasswordTouched] = useState(false);

  const [loading, setLoading] = useState(false);

  const emailError = useMemo(() => validateEmail(email), [email]);
  const passwordError = useMemo(() => validatePassword(password), [password]);

  const isFormValid = !emailError && !passwordError;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    setEmailTouched(true);
    setPasswordTouched(true);

    if (!isFormValid) {
      showToast("Проверь email и пароль", "error");
      return;
    }

    try {
      setLoading(true);
      await register(email.trim(), password);
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

        <form onSubmit={handleSubmit} noValidate>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => setEmailTouched(true)}
            autoComplete="email"
          />

          {emailTouched && emailError && (
            <p className="form-error">{emailError}</p>
          )}

          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onBlur={() => setPasswordTouched(true)}
            autoComplete="new-password"
          />

          {passwordTouched && passwordError && (
            <p className="form-error">{passwordError}</p>
          )}

          <p className="password-hint">
            Пароль должен содержать минимум 8 символов, заглавную и строчную букву,
            цифру и специальный символ.
          </p>

          <button className="button" type="submit" disabled={loading || !isFormValid}>
            {loading ? "Создаём..." : "Зарегистрироваться"}
          </button>
        </form>

        <p className="muted">
          Уже есть аккаунт?{" "}
          <Link to="/login">
            <strong>Войти</strong>
          </Link>
        </p>
      </div>
    </Layout>
  );
}