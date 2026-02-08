import React, { useState } from 'react';
import '../css/Header.css';
import Sidebar from './Sidebar';

function Header() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const closeSidebar = () => {
        setIsSidebarOpen(false);
    };

    return (
        <>
            <header className='header'>
                <h1 className='header-title'>LIBRARY MANAGER</h1>

                <button
                    className='hamburger-menu'
                    onClick={toggleSidebar}
                >
                    <div className='hamburger-line'></div>
                    <div className='hamburger-line'></div>
                    <div className='hamburger-line'></div>
                </button>
            </header>
            
            <Sidebar isOpen = {isSidebarOpen} onClose={closeSidebar} />
        </>
    );
}

export default Header;