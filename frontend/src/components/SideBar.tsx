'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

function Sidebar({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const { isAuthenticated, logout, user, checkAuth } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isOpen) {
      checkAuth();
    }
  }, [isOpen, checkAuth]);

  const handleLogout = () => {
    logout();
    onClose();
    router.push('/');
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
              <Link href="/" className="sidebar-link" onClick={onClose}>
                Home
              </Link>
              <Link href="/admin" className="sidebar-link" onClick={onClose}>
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
              <Link href="/" className="sidebar-link" onClick={onClose}>
                Home
              </Link>
              <Link href="/login" className="sidebar-link" onClick={onClose}>
                Login
              </Link>
              <Link href="/register" className="sidebar-link" onClick={onClose}>
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
