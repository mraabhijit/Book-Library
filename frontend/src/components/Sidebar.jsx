import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../css/Sidebar.css';
import { useAuth } from '../context/AuthContext';

function Sidebar({ isOpen, onClose }) {
  const { isAuthenticated, logout, user, checkAuth } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      checkAuth();
    }
  }, [isOpen, checkAuth]);

  const handleLogout = () => {
    logout();
    onClose();
    navigate('/');
  };

  return (
    <>
      {/* Overlay - click to close sidebar */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}

      {/* Sidebar */}
      <div className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2>Menu</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        {user && (
          <div className="user-info">
            <p className="sidebar-text">{user.username}</p>
          </div>
        )}

        <nav className="sidebar-nav">
          {isAuthenticated ? (
            <>
              <Link to="/" className="sidebar-link" onClick={onClose}>
                Home
              </Link>
              <Link to="/admin" className="sidebar-link" onClick={onClose}>
                Admin
              </Link>
              <button
                className="sidebar-link logout-btn"
                onClick={handleLogout}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/" className="sidebar-link" onClick={onClose}>
                Home
              </Link>
              <Link to="/login" className="sidebar-link" onClick={onClose}>
                Login
              </Link>
              <Link to="/register" className="sidebar-link" onClick={onClose}>
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </>
  );
}

export default Sidebar;
