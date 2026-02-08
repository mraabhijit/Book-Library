import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';


function RouteLogger() {
  const location = useLocation();

  useEffect(() => {
    console.log('Navigated to: ', location.pathname);
  }, [location]);

  return null;
}


function App() {

  return (
    <Router>
      <div className='app'>
        <RouteLogger />
        <Header />
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/login' element={<Login />} />
          <Route path='/register' element={<Register />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
