import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();

  function handleLogout() {
    logout();
    showToast("Вы вышли из аккаунта", "info");
    navigate("/login", { replace: true });
  }

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">
          Music Analyzer ✨
        </Link>

        {isAuthenticated && (
          <nav className="nav-links">
            <Link className="badge" to="/">
              Dashboard
            </Link>
            <span className="nav-email">{user?.email}</span>
            <button onClick={handleLogout} className="button secondary">
              Выйти
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}