import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import StudentLogin from './student-dashboard/StudentLogin';
import StudentRegister from './student-dashboard/StudentRegister';
import StudentDashboard from './student-dashboard/StudentDashboard';
import './App.css';
import './StudentApp.css';

// ─── Role Selector (Landing Page) ───
function RoleSelector() {
    return (
        <div className="role-selector-wrapper">
            <div className="role-selector-card">
                <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🛡️</div>
                <h1>EduShield AI</h1>
                <p className="role-subtitle">Federated Learning — Privacy-Preserving Smart Campus</p>
                <div className="role-cards">
                    <Link to="/student/login" className="role-card">
                        <span className="role-icon">🎓</span>
                        <h3>Student Portal</h3>
                        <p>View your attendance, marks, risk predictions, and study plans</p>
                    </Link>
                    <Link to="/login" className="role-card">
                        <span className="role-icon">🔧</span>
                        <h3>Admin Dashboard</h3>
                        <p>Manage federated training, view models, and compare approaches</p>
                    </Link>
                </div>
            </div>
        </div>
    );
}

function App() {
    // ─── Admin Auth State ───
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // ─── Student Auth State ───
    const [studentAuth, setStudentAuth] = useState(false);
    const [studentData, setStudentData] = useState(null);
    const [studentAuthView, setStudentAuthView] = useState('login'); // 'login' or 'register'

    useEffect(() => {
        // Admin auth check
        const auth = localStorage.getItem('authenticated');
        if (auth === 'true') {
            setIsAuthenticated(true);
        }

        // Student auth check
        const token = localStorage.getItem('student_token');
        const data = localStorage.getItem('student_data');
        if (token && data) {
            setStudentAuth(true);
            setStudentData(JSON.parse(data));
        }
    }, []);

    // ─── Admin handlers ───
    const handleLogin = () => {
        localStorage.setItem('authenticated', 'true');
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        localStorage.removeItem('authenticated');
        setIsAuthenticated(false);
    };

    // ─── Student handlers ───
    const handleStudentLogin = (student) => {
        setStudentAuth(true);
        setStudentData(student);
    };

    const handleStudentLogout = () => {
        localStorage.removeItem('student_token');
        localStorage.removeItem('student_data');
        setStudentAuth(false);
        setStudentData(null);
        setStudentAuthView('login');
    };

    // ─── Student Auth Page (Login or Register) ───
    const StudentAuthPage = () => {
        if (studentAuthView === 'register') {
            return (
                <StudentRegister
                    onRegister={handleStudentLogin}
                    onSwitchToLogin={() => setStudentAuthView('login')}
                />
            );
        }
        return (
            <StudentLogin
                onLogin={handleStudentLogin}
                onSwitchToRegister={() => setStudentAuthView('register')}
            />
        );
    };

    return (
        <Router>
            <div className="App">
                <Routes>
                    {/* ─── Landing / Role Selector ─── */}
                    <Route path="/" element={<RoleSelector />} />

                    {/* ─── Admin Routes (UNCHANGED) ─── */}
                    <Route
                        path="/login"
                        element={
                            isAuthenticated ?
                                <Navigate to="/dashboard" /> :
                                <Login onLogin={handleLogin} />
                        }
                    />
                    <Route
                        path="/dashboard"
                        element={
                            isAuthenticated ?
                                <Dashboard onLogout={handleLogout} /> :
                                <Navigate to="/login" />
                        }
                    />

                    {/* ─── Student Routes (NEW) ─── */}
                    <Route
                        path="/student/login"
                        element={
                            studentAuth ?
                                <Navigate to="/student/dashboard" /> :
                                <StudentAuthPage />
                        }
                    />
                    <Route
                        path="/student/register"
                        element={
                            studentAuth ?
                                <Navigate to="/student/dashboard" /> :
                                <StudentRegister
                                    onRegister={handleStudentLogin}
                                    onSwitchToLogin={() => setStudentAuthView('login')}
                                />
                        }
                    />
                    <Route
                        path="/student/dashboard"
                        element={
                            studentAuth && studentData ?
                                <StudentDashboard
                                    student={studentData}
                                    onLogout={handleStudentLogout}
                                /> :
                                <Navigate to="/student/login" />
                        }
                    />

                    {/* ─── Fallback ─── */}
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
