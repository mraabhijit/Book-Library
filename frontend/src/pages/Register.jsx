import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../css/Register.css';


function Register() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);


    const handleSubmit = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        setError(null);

        // API call goes here
        console.log('Registration attempt:', { username, email });

        setTimeout(() => {
            setLoading(true);
            alert('Registration functionality coming soon!');
        }, 1000);
    };

    return (
        <div className='register-container'>
            <div className='register-card'>
                <h2 className='register-title'>Register</h2>

                <form onSubmit={handleSubmit} className='register-form'>
                    <div className='form-group'>
                        <label htmlFor="fullName">Full Name</label>
                        <input 
                            type="text"
                            id='fullName'
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder='Enter your full name'
                            className='form-input'
                        />
                    </div>

                    <div className='form-group'>
                        <label htmlFor="username">Username</label>
                        <input 
                            type="text"
                            id='username'
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder='Enter your username'
                            required
                            className='form-input'
                        />
                    </div>

                    <div className='form-group'>
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id='email'
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder='Enter your email'
                            required
                            className='form-input'
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
                            minLength="8"
                            className="form-input"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirm your password"
                            required
                            minLength="8"
                            className="form-input"
                        />
                    </div>

                    {error && <div className='error-message'>{error}</div>}

                    <button
                        type='submit'
                        className='submit-button'
                        disabled={loading}
                    >
                        {loading ? 'Registering...' : 'Register'}
                    </button>
                </form>

                <p className='redirect-text'>
                    Already have an account? <Link to='/login' className='redirect-link'>Login</Link>
                </p>
            </div>
        </div>
    );
}

export default Register;