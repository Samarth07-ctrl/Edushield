import React, { useState, useEffect } from 'react';
import { analyzeSkillGap, getRoles } from '../services/api';

function SkillGap() {
    const [roles, setRoles] = useState([]);
    const [selectedRole, setSelectedRole] = useState('backend_engineer');
    const [skills, setSkills] = useState({});
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        loadRoles();
    }, []);

    const loadRoles = async () => {
        try {
            const data = await getRoles();
            setRoles(data.roles || []);
            if (data.roles?.length > 0) {
                initSkills(data.roles[0].skills);
            }
        } catch (err) {
            setError('Failed to load roles');
        }
    };

    const initSkills = (skillList) => {
        const init = {};
        skillList.forEach(s => { init[s] = 50; });
        setSkills(init);
    };

    const handleRoleChange = (roleKey) => {
        setSelectedRole(roleKey);
        const role = roles.find(r => r.key === roleKey);
        if (role) initSkills(role.skills);
        setResult(null);
    };

    const handleSkillChange = (skill, value) => {
        setSkills(prev => ({ ...prev, [skill]: parseInt(value) || 0 }));
    };

    const handleAnalyze = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await analyzeSkillGap(skills, selectedRole);
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.error || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };

    const getPriorityColor = (p) => {
        if (p === 'high') return '#ff4757';
        if (p === 'medium') return '#ffa502';
        return '#2ed573';
    };

    return (
        <div className="career-section">
            <div className="career-card">
                <div className="card-header">
                    <h3>🎯 Skill Gap Analysis</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                        Compare your skills against job role requirements
                    </p>
                </div>
                <div className="card-body">
                    {/* Role Selector */}
                    <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                        <label>Target Role</label>
                        <select
                            value={selectedRole}
                            onChange={(e) => handleRoleChange(e.target.value)}
                            className="career-select"
                        >
                            {roles.map(r => (
                                <option key={r.key} value={r.key}>{r.title}</option>
                            ))}
                        </select>
                    </div>

                    {/* Skill Sliders */}
                    <div className="skill-sliders">
                        {Object.entries(skills).map(([skill, value]) => (
                            <div key={skill} className="slider-item">
                                <div className="slider-header">
                                    <span className="slider-label">{skill.replace(/_/g, ' ')}</span>
                                    <span className="slider-value">{value}</span>
                                </div>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={value}
                                    onChange={(e) => handleSkillChange(skill, e.target.value)}
                                    className="career-slider"
                                />
                            </div>
                        ))}
                    </div>

                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="btn btn-primary career-btn"
                    >
                        {loading ? '⏳ Analyzing...' : '🔍 Analyze Gaps'}
                    </button>

                    {error && <div className="career-error">{error}</div>}
                </div>
            </div>

            {/* Results */}
            {result && (
                <>
                    {/* Readiness Overview */}
                    <div className="career-card">
                        <div className="card-header">
                            <h3>📊 Gap Results — {result.target_role}</h3>
                            <div className="readiness-badge" style={{
                                background: result.readiness_percentage >= 70 ? '#2ed573' :
                                    result.readiness_percentage >= 40 ? '#ffa502' : '#ff4757'
                            }}>
                                {result.readiness_percentage}% Ready
                            </div>
                        </div>
                        <div className="card-body">
                            <div className="gap-overview">
                                <div className="overview-stat">
                                    <div className="stat-number">{result.skills_met}</div>
                                    <div className="stat-desc">Skills Met</div>
                                </div>
                                <div className="overview-stat">
                                    <div className="stat-number">{result.total_skills - result.skills_met}</div>
                                    <div className="stat-desc">Gaps Found</div>
                                </div>
                                <div className="overview-stat">
                                    <div className="stat-number">{result.total_skills}</div>
                                    <div className="stat-desc">Total Skills</div>
                                </div>
                            </div>

                            {/* Gap Table */}
                            <table className="career-table">
                                <thead>
                                    <tr>
                                        <th>Skill</th>
                                        <th>Required</th>
                                        <th>Current</th>
                                        <th>Gap</th>
                                        <th>Priority</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.entries(result.skill_gaps)
                                        .sort((a, b) => b[1].gap - a[1].gap)
                                        .map(([skill, info]) => (
                                            <tr key={skill} className={info.met ? 'row-met' : ''}>
                                                <td>{skill.replace(/_/g, ' ')}</td>
                                                <td>{info.required}</td>
                                                <td>{info.current}</td>
                                                <td>
                                                    <span style={{ color: info.gap > 0 ? '#ff6b81' : '#2ed573', fontWeight: 600 }}>
                                                        {info.gap > 0 ? `-${info.gap}` : '✓'}
                                                    </span>
                                                </td>
                                                <td>
                                                    <span className="priority-pill" style={{ background: getPriorityColor(info.priority) }}>
                                                        {info.priority}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Learning Roadmap */}
                    {result.roadmap && result.roadmap.length > 0 && (
                        <div className="career-card">
                            <div className="card-header">
                                <h3>🗺️ Learning Roadmap</h3>
                            </div>
                            <div className="card-body">
                                <div className="roadmap">
                                    {result.roadmap.map((item, idx) => (
                                        <div key={idx} className="roadmap-item">
                                            <div className="roadmap-week">
                                                <span className="week-badge">{item.week}</span>
                                                {item.priority && (
                                                    <span className="priority-pill small" style={{
                                                        background: getPriorityColor(item.priority)
                                                    }}>
                                                        {item.priority}
                                                    </span>
                                                )}
                                            </div>
                                            <div className="roadmap-content">
                                                <div className="roadmap-focus">{item.focus}</div>
                                                <div className="roadmap-action">{item.action}</div>
                                                <div className="roadmap-hours">{item.hours_per_week}h/week</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default SkillGap;
