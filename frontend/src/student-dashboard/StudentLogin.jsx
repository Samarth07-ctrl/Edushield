import React, { useState } from 'react';
import { loginStudent } from '../services/authApi';

function StudentLogin({ onLogin, onSwitchToRegister }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const data = await loginStudent(email, password);
            localStorage.setItem('student_token', data.token);
            localStorage.setItem('student_data', JSON.stringify(data.student));
            onLogin(data.student);
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed. Check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="student-auth-wrapper">
            <div className="student-auth-card">
                <div className="auth-logo">
                    <span className="auth-logo-icon">🛡️</span>
                    <h1 className="auth-title">EduShield AI</h1>
                    <p className="auth-subtitle">Student Portal — Privacy-Preserving Learning Analytics</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            placeholder="you@campus.edu"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            autoFocus
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {error && <div className="auth-error">{error}</div>}

                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? (
                            <><span className="spinner"></span> Signing in...</>
                        ) : (
                            'Sign In'
                        )}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Don't have an account?{' '}
                        <button className="link-btn" onClick={onSwitchToRegister}>
                            Register here
                        </button>
                    </p>
                </div>

                <div className="auth-privacy-badge">
                    <span>🔒</span>
                    <span>Your data stays on your campus node — never shared centrally</span>
                </div>
            </div>
        </div>
    );
}

export default StudentLogin;
