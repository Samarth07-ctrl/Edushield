import React, { useState, useEffect, useCallback } from 'react';
import { predictRisk, getPlacementReadiness, getStudyPlan, getAttendance, getMarks } from '../services/studentApi';

function StudentDashboard({ student, onLogout }) {
    const [activeTab, setActiveTab] = useState('overview');
    const [riskData, setRiskData] = useState(null);
    const [placementData, setPlacementData] = useState(null);
    const [studyPlanData, setStudyPlanData] = useState(null);
    const [attendanceData, setAttendanceData] = useState(null);
    const [marksData, setMarksData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Map student_id string → numeric for DB lookup
    const numericId = parseInt(student.student_id) || 1;
    const clientId = student.client_id || 1;

    const loadAllData = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const [riskRes, placementRes, planRes, attendRes, marksRes] = await Promise.allSettled([
                predictRisk(clientId, numericId),
                getPlacementReadiness(clientId, numericId),
                getStudyPlan(clientId, numericId),
                getAttendance(clientId, numericId),
                getMarks(clientId, numericId)
            ]);

            if (riskRes.status === 'fulfilled') setRiskData(riskRes.value);
            if (placementRes.status === 'fulfilled') setPlacementData(placementRes.value);
            if (planRes.status === 'fulfilled') setStudyPlanData(planRes.value);
            if (attendRes.status === 'fulfilled') setAttendanceData(attendRes.value.data);
            if (marksRes.status === 'fulfilled') setMarksData(marksRes.value.data);

            // Check if we got any data at all
            const anyData = [riskRes, placementRes, planRes, attendRes, marksRes].some(r => r.status === 'fulfilled');
            if (!anyData) {
                setError(`No data found for Student ID ${numericId} on Client ${clientId}. Try a different student ID.`);
            }
        } catch (err) {
            setError('Failed to load data. Ensure the Client API server is running on port 5002.');
        } finally {
            setLoading(false);
        }
    }, [clientId, numericId]);

    useEffect(() => {
        loadAllData();
    }, [loadAllData]);

    // ────────────────── Render Helpers ──────────────────

    const getRiskColor = (level) => {
        switch (level) {
            case 'high': return '#ff4757';
            case 'medium': return '#ffa502';
            case 'low': return '#2ed573';
            default: return '#a0a0a0';
        }
    };

    const getGradeColor = (grade) => {
        if (grade === 'A+' || grade === 'A') return '#2ed573';
        if (grade === 'B') return '#7bed9f';
        if (grade === 'C') return '#ffa502';
        if (grade === 'D') return '#ff6348';
        return '#ff4757';
    };

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'critical': return '#ff4757';
            case 'high': return '#ffa502';
            case 'medium': return '#3498db';
            case 'maintain': return '#2ed573';
            default: return '#a0a0a0';
        }
    };

    const getReadinessColor = (level) => {
        switch (level) {
            case 'excellent': return '#2ed573';
            case 'good': return '#7bed9f';
            case 'moderate': return '#ffa502';
            case 'needs_improvement': return '#ff4757';
            default: return '#a0a0a0';
        }
    };

    // ────────────────── Overview Tab ──────────────────
    const renderOverview = () => (
        <div className="student-grid">
            {/* Risk Card */}
            <div className="student-card risk-card">
                <div className="card-header">
                    <h3>🎯 Attendance Risk</h3>
                    {riskData && (
                        <span className="risk-badge" style={{ background: getRiskColor(riskData.risk_level) }}>
                            {riskData.risk_level.toUpperCase()}
                        </span>
                    )}
                </div>
                {riskData ? (
                    <div className="card-body">
                        <div className="risk-meter">
                            <div className="meter-fill" style={{
                                width: `${riskData.risk_score}%`,
                                background: `linear-gradient(90deg, #2ed573, #ffa502, #ff4757)`,
                            }}></div>
                            <span className="meter-label">{riskData.risk_score}%</span>
                        </div>
                        <div className="risk-factors">
                            {riskData.factors && Object.entries(riskData.factors).map(([key, val]) => (
                                <div key={key} className="factor-item">
                                    <span className="factor-label">{key.replace(/_/g, ' ')}</span>
                                    <span className="factor-value">
                                        {typeof val === 'number' ? (key.includes('rate') || key.includes('participation') ? `${val}%` : val) : val}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="card-body empty">No risk data available</div>
                )}
            </div>

            {/* Placement Readiness Card */}
            <div className="student-card placement-card">
                <div className="card-header">
                    <h3>🚀 Placement Readiness</h3>
                    {placementData && (
                        <span className="risk-badge" style={{ background: getReadinessColor(placementData.level) }}>
                            {placementData.level.replace('_', ' ').toUpperCase()}
                        </span>
                    )}
                </div>
                {placementData ? (
                    <div className="card-body">
                        <div className="readiness-score">
                            <div className="score-circle" style={{ '--score': placementData.readiness_score }}>
                                <span className="score-value">{placementData.readiness_score}%</span>
                            </div>
                        </div>
                        <div className="breakdown-bars">
                            {placementData.breakdown && Object.entries(placementData.breakdown).map(([key, val]) => (
                                <div key={key} className="bar-item">
                                    <div className="bar-label">
                                        <span>{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                                        <span>{val}%</span>
                                    </div>
                                    <div className="bar-track">
                                        <div className="bar-fill" style={{
                                            width: `${val}%`,
                                            background: val >= 70 ? '#2ed573' : val >= 50 ? '#ffa502' : '#ff4757'
                                        }}></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="card-body empty">No placement data available</div>
                )}
            </div>

            {/* Attendance Overview Card */}
            <div className="student-card attendance-card">
                <div className="card-header">
                    <h3>📊 Attendance Overview</h3>
                </div>
                {attendanceData ? (
                    <div className="card-body">
                        <div className="stat-grid">
                            <div className="stat-item">
                                <div className="stat-value" style={{
                                    color: attendanceData.attendance_rate >= 0.75 ? '#2ed573' : '#ff4757'
                                }}>
                                    {(attendanceData.attendance_rate * 100).toFixed(1)}%
                                </div>
                                <div className="stat-label">Attendance</div>
                            </div>
                            <div className="stat-item">
                                <div className="stat-value">{attendanceData.absences}</div>
                                <div className="stat-label">Absences</div>
                            </div>
                            <div className="stat-item">
                                <div className="stat-value">{attendanceData.study_hours?.toFixed(1)}h</div>
                                <div className="stat-label">Study Hours/Day</div>
                            </div>
                            <div className="stat-item">
                                <div className="stat-value">{(attendanceData.participation * 100).toFixed(0)}%</div>
                                <div className="stat-label">Participation</div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="card-body empty">No attendance data available</div>
                )}
            </div>

            {/* Marks Card */}
            <div className="student-card marks-card">
                <div className="card-header">
                    <h3>📝 Academic Scores</h3>
                </div>
                {marksData ? (
                    <div className="card-body">
                        <div className="marks-list">
                            {[
                                { subject: 'Mathematics', score: marksData.math_score },
                                { subject: 'Science', score: marksData.science_score },
                                { subject: 'English', score: marksData.english_score },
                            ].map((item) => (
                                <div key={item.subject} className="mark-item">
                                    <span className="mark-subject">{item.subject}</span>
                                    <div className="mark-bar-wrapper">
                                        <div className="mark-bar" style={{
                                            width: `${Math.min(item.score, 100)}%`,
                                            background: item.score >= 70 ? 'linear-gradient(90deg, #2ed573, #7bed9f)' :
                                                item.score >= 50 ? 'linear-gradient(90deg, #ffa502, #eccc68)' :
                                                    'linear-gradient(90deg, #ff4757, #ff6b81)'
                                        }}></div>
                                    </div>
                                    <span className="mark-score">{item.score?.toFixed(1)}</span>
                                </div>
                            ))}
                            <div className="mark-item meta">
                                <span>Assignment Rate</span>
                                <span className="mark-score">{(marksData.assignment_rate * 100).toFixed(0)}%</span>
                            </div>
                            <div className="mark-item meta">
                                <span>Quiz Average</span>
                                <span className="mark-score">{marksData.quiz_avg?.toFixed(1)}</span>
                            </div>
                            {marksData.weak_subject && marksData.weak_subject !== 'none' && (
                                <div className="weak-subject-tag">
                                    ⚠️ Focus Area: <strong>{marksData.weak_subject}</strong>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="card-body empty">No marks data available</div>
                )}
            </div>
        </div>
    );

    // ────────────────── Study Planner Tab ──────────────────
    const renderStudyPlanner = () => (
        <div className="study-planner">
            {studyPlanData ? (
                <>
                    <div className="planner-summary">
                        <div className="summary-item">
                            <span className="summary-icon">📚</span>
                            <div>
                                <div className="summary-value">{studyPlanData.total_current_hours}h</div>
                                <div className="summary-label">Current Weekly Hours</div>
                            </div>
                        </div>
                        <div className="summary-item">
                            <span className="summary-icon">🎯</span>
                            <div>
                                <div className="summary-value">{studyPlanData.total_recommended_hours}h</div>
                                <div className="summary-label">Recommended Hours</div>
                            </div>
                        </div>
                        <div className="summary-item">
                            <span className="summary-icon">🔍</span>
                            <div>
                                <div className="summary-value" style={{ textTransform: 'capitalize' }}>
                                    {studyPlanData.focus_area}
                                </div>
                                <div className="summary-label">Focus Area</div>
                            </div>
                        </div>
                    </div>

                    <div className="planner-cards">
                        {studyPlanData.weekly_plan?.map((item, idx) => (
                            <div key={idx} className="plan-card">
                                <div className="plan-card-header">
                                    <h4>{item.subject}</h4>
                                    <span className="priority-badge" style={{
                                        background: getPriorityColor(item.priority)
                                    }}>
                                        {item.priority}
                                    </span>
                                </div>
                                <div className="plan-card-body">
                                    <div className="plan-stats">
                                        <div className="plan-stat">
                                            <span className="plan-stat-label">Score</span>
                                            <span className="plan-stat-value">{item.current_score}</span>
                                        </div>
                                        <div className="plan-stat">
                                            <span className="plan-stat-label">Current</span>
                                            <span className="plan-stat-value">{item.current_hours}h</span>
                                        </div>
                                        <div className="plan-stat recommended">
                                            <span className="plan-stat-label">Target</span>
                                            <span className="plan-stat-value">{item.recommended_hours}h</span>
                                        </div>
                                    </div>
                                    {item.tips && (
                                        <div className="plan-tips">
                                            {item.tips.map((tip, tidx) => (
                                                <div key={tidx} className="tip-item">
                                                    <span>💡</span>
                                                    <span>{tip}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                <div className="empty-state">
                    <p>No study plan data available. Make sure the Client API is running.</p>
                </div>
            )}
        </div>
    );

    // ────────────────── Skills Tab ──────────────────
    const renderSkills = () => (
        <div className="skills-section">
            {placementData?.skills ? (
                <div className="skills-grid">
                    {Object.entries(placementData.skills).map(([skill, data]) => (
                        <div key={skill} className="skill-card">
                            <div className="skill-header">
                                <h4>{skill.charAt(0).toUpperCase() + skill.slice(1)}</h4>
                                <span className="skill-grade" style={{
                                    color: getGradeColor(data.grade)
                                }}>{data.grade}</span>
                            </div>
                            <div className="skill-score">{data.score}%</div>
                            <div className="skill-bar-track">
                                <div className="skill-bar-fill" style={{
                                    width: `${data.score}%`,
                                    background: getGradeColor(data.grade)
                                }}></div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <p>No skills data available.</p>
                </div>
            )}
        </div>
    );

    // ────────────────── Recommendations Tab ──────────────────
    const renderRecommendations = () => (
        <div className="recommendations-section">
            {riskData?.recommendations ? (
                <div className="rec-list">
                    {riskData.recommendations.map((rec, idx) => (
                        <div key={idx} className={`rec-card priority-${rec.priority}`}>
                            <div className="rec-header">
                                <span className="rec-area">{rec.area}</span>
                                <span className="rec-priority" style={{
                                    background: rec.priority === 'high' ? '#ff4757' :
                                        rec.priority === 'medium' ? '#ffa502' : '#2ed573'
                                }}>
                                    {rec.priority}
                                </span>
                            </div>
                            <p className="rec-text">{rec.suggestion}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <p>No recommendations available.</p>
                </div>
            )}
        </div>
    );

    // ────────────────── Tab Content Router ──────────────────
    const renderContent = () => {
        if (loading) {
            return (
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading your data from local campus node...</p>
                </div>
            );
        }
        if (error) {
            return (
                <div className="error-state">
                    <span className="error-icon">⚠️</span>
                    <p>{error}</p>
                    <button className="auth-btn" onClick={loadAllData}>Retry</button>
                </div>
            );
        }

        switch (activeTab) {
            case 'overview': return renderOverview();
            case 'study-planner': return renderStudyPlanner();
            case 'skills': return renderSkills();
            case 'recommendations': return renderRecommendations();
            default: return renderOverview();
        }
    };

    // ────────────────── Main Render ──────────────────
    return (
        <div className="student-dashboard">
            <aside className="student-sidebar">
                <div className="sidebar-header">
                    <h2>🛡️ EduShield</h2>
                    <p className="sidebar-subtitle">Student Portal</p>
                </div>

                <div className="student-profile">
                    <div className="profile-avatar">
                        {student.name?.charAt(0).toUpperCase() || 'S'}
                    </div>
                    <div className="profile-info">
                        <div className="profile-name">{student.name}</div>
                        <div className="profile-dept">{student.department}</div>
                        <div className="profile-id">ID: {student.student_id}</div>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {[
                        { key: 'overview', icon: '📊', label: 'Overview' },
                        { key: 'study-planner', icon: '📚', label: 'Study Planner' },
                        { key: 'skills', icon: '💪', label: 'Skills' },
                        { key: 'recommendations', icon: '💡', label: 'Recommendations' },
                    ].map((tab) => (
                        <div
                            key={tab.key}
                            className={`nav-item ${activeTab === tab.key ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.key)}
                        >
                            <span>{tab.icon}</span>
                            <span>{tab.label}</span>
                        </div>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="privacy-indicator">
                        <span className="status-dot"></span>
                        <span>Data processed locally</span>
                    </div>
                    <button onClick={onLogout} className="btn btn-secondary" style={{ width: '100%' }}>
                        Logout
                    </button>
                </div>
            </aside>

            <main className="student-main">
                <div className="content-header">
                    <div>
                        <h1>
                            {activeTab === 'overview' && '📊 Dashboard Overview'}
                            {activeTab === 'study-planner' && '📚 Study Planner'}
                            {activeTab === 'skills' && '💪 Skills Analysis'}
                            {activeTab === 'recommendations' && '💡 Recommendations'}
                        </h1>
                        <p className="header-subtitle">
                            Privacy-preserving analytics from your campus node (Client {clientId})
                        </p>
                    </div>
                    <button className="refresh-btn" onClick={loadAllData} title="Refresh data">
                        🔄
                    </button>
                </div>

                {renderContent()}
            </main>
        </div>
    );
}

export default StudentDashboard;
