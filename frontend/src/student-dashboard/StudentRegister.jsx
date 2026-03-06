import React, { useState } from 'react';
import { registerStudent } from '../services/authApi';

function StudentRegister({ onRegister, onSwitchToLogin }) {
    const [form, setForm] = useState({
        student_id: '',
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        department: 'Computer Science'
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const departments = [
        'Computer Science',
        'Electronics',
        'Mechanical',
        'Civil',
        'Information Technology'
    ];

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (form.password !== form.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (form.password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            const data = await registerStudent({
                student_id: form.student_id,
                name: form.name,
                email: form.email,
                password: form.password,
                department: form.department
            });

            localStorage.setItem('student_token', data.token);
            localStorage.setItem('student_data', JSON.stringify(data.student));
            onRegister(data.student);
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="student-auth-wrapper">
            <div className="student-auth-card register-card">
                <div className="auth-logo">
                    <span className="auth-logo-icon">🛡️</span>
                    <h1 className="auth-title">EduShield AI</h1>
                    <p className="auth-subtitle">Create your Student Account</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="student_id">Student ID</label>
                            <input
                                id="student_id"
                                name="student_id"
                                type="text"
                                placeholder="e.g. 5"
                                value={form.student_id}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="name">Full Name</label>
                            <input
                                id="name"
                                name="name"
                                type="text"
                                placeholder="John Doe"
                                value={form.name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="reg-email">Email</label>
                        <input
                            id="reg-email"
                            name="email"
                            type="email"
                            placeholder="you@campus.edu"
                            value={form.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="department">Department</label>
                        <select
                            id="department"
                            name="department"
                            value={form.department}
                            onChange={handleChange}
                        >
                            {departments.map((d) => (
                                <option key={d} value={d}>{d}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="reg-password">Password</label>
                            <input
                                id="reg-password"
                                name="password"
                                type="password"
                                placeholder="Min 6 characters"
                                value={form.password}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="confirmPassword">Confirm Password</label>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                placeholder="Confirm password"
                                value={form.confirmPassword}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    {error && <div className="auth-error">{error}</div>}

                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? (
                            <><span className="spinner"></span> Creating account...</>
                        ) : (
                            'Create Account'
                        )}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Already have an account?{' '}
                        <button className="link-btn" onClick={onSwitchToLogin}>
                            Sign in
                        </button>
                    </p>
                </div>

                <div className="auth-privacy-badge">
                    <span>🔒</span>
                    <span>Your academic data is processed locally — never sent to a central server</span>
                </div>
            </div>
        </div>
    );
}

export default StudentRegister;
