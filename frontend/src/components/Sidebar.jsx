import React from 'react';
import { Link } from 'react-router-dom'
import '../css/Sidebar.css';

function Sidebar({ isOpen, onClose }) {
    return (
        <>
            {/* Overlay - click to close sidebar */}
            {isOpen && <div className='sidebar-overlay' onClick={onClose}></div>}

            {/* Sidebar */}
            <div className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
                <div className='sidebar-header'>
                    <h2>Menu</h2>
                    <button className='close-button' onClick={onClose}>
                       ✕ 
                    </button>
                </div>

                <nav className="sidebar-nav">
                    <Link to="/" className="sidebar-link" onClick={onClose}>
                        Home
                    </Link>
                    <Link to="/login" className="sidebar-link" onClick={onClose}>
                        Login
                    </Link>
                    <Link to="/register" className="sidebar-link" onClick={onClose}>
                        Register
                    </Link>
                </nav>
            </div>
        </>
    );
}

export default Sidebar;