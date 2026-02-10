import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../css/Login.css';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload

    setLoading(true);
    setError(null);

    try {
      // Call Login API
      const response = await authAPI.login({ username, password });

      console.log('Login successful');

      localStorage.setItem('authToken', response.data.access_token);
      localStorage.setItem('tokenType', response.data.token_type);

      // Get current user info
      const userResponse = await authAPI.getCurrentUser();
      login(response.data.access_token, userResponse.data);

      // Redirect to home page
      navigate('/admin');
    } catch (err) {
      console.error('Login error: ', err);

      if (err.response?.status === 401) {
        setError('Incorrect email or password');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(err.message || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2 className="login-title">Login</h2>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Email</label>
            <input
              type="email"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your email"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              className="form-input"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="redirect-text">
          Don't have an account?{' '}
          <Link to="/register" className="redirect-link">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
