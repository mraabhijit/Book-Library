import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../css/Login.css';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();  // Prevent page reload

        setLoading(true);
        setError(null);

        // API call goes here
        console.log('Login attempt: ', { username, password });
        
        setTimeout(() => {
            setLoading(false);
            alert('Login functionality coming shortly!');
        }, 1000);
    };

    return (
        <div className='login-container'>
            <div className='login-card'>
                <h2 className='login-title'>Login</h2>
                
                <form onSubmit={handleSubmit} className='login-form'>
                    <div className='form-group'>
                        <label htmlFor="username">Email</label>
                        <input 
                            type="email"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder='Enter your email'
                            required
                            className='form-input'
                        />
                    </div>

                    <div className='form-group'>
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder='Enter your password'
                            required
                            className='form-input'
                        />
                    </div>

                    {error && <div className='error-message'>{error}</div>}

                    <button
                        type='submit'
                        className='submit-button'
                        disabled={loading}
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <p className='redirect-text'>
                    Don't have an account? <Link to='/register' className='redirect-link'>Register</Link>
                </p>
            </div>
        </div>
    );
}

export default Login;
