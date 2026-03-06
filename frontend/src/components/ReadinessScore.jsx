import React, { useState } from 'react';
import { getReadinessScore } from '../services/api';

function ReadinessScore() {
    const [profile, setProfile] = useState({
        gpa: 7.0,
        dsa_score: 55,
        projects: 2,
        internships: 1,
        communication_score: 60,
        coding_score: 55
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fields = [
        { key: 'gpa', label: 'GPA (0–10)', min: 0, max: 10, step: 0.1 },
        { key: 'dsa_score', label: 'DSA Score (0–100)', min: 0, max: 100, step: 1 },
        { key: 'projects', label: 'Projects', min: 0, max: 15, step: 1 },
        { key: 'internships', label: 'Internships', min: 0, max: 5, step: 1 },
        { key: 'communication_score', label: 'Communication (0–100)', min: 0, max: 100, step: 1 },
        { key: 'coding_score', label: 'Coding Score (0–100)', min: 0, max: 100, step: 1 },
    ];

    const handleChange = (key, value) => {
        setProfile(prev => ({ ...prev, [key]: parseFloat(value) || 0 }));
    };

    const handlePredict = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await getReadinessScore(profile);
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.error || 'Prediction failed');
        } finally {
            setLoading(false);
        }
    };

    const getGaugeRotation = (score) => {
        return (score / 100) * 180 - 90; // -90 to 90 degrees
    };

    return (
        <div className="career-section">
            <div className="career-card">
                <div className="card-header">
                    <h3>🏆 Interview Readiness Score</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                        ML-powered placement probability using Logistic Regression
                    </p>
                </div>
                <div className="card-body">
                    <div className="profile-inputs">
                        {fields.map(f => (
                            <div key={f.key} className="slider-item">
                                <div className="slider-header">
                                    <span className="slider-label">{f.label}</span>
                                    <span className="slider-value">{profile[f.key]}</span>
                                </div>
                                <input
                                    type="range"
                                    min={f.min}
                                    max={f.max}
                                    step={f.step}
                                    value={profile[f.key]}
                                    onChange={(e) => handleChange(f.key, e.target.value)}
                                    className="career-slider"
                                />
                            </div>
                        ))}
                    </div>

                    <button
                        onClick={handlePredict}
                        disabled={loading}
                        className="btn btn-primary career-btn"
                    >
                        {loading ? '⏳ Predicting...' : '🎯 Calculate Readiness'}
                    </button>

                    {error && <div className="career-error">{error}</div>}
                </div>
            </div>

            {/* Results */}
            {result && (
                <div className="career-card">
                    <div className="card-header">
                        <h3>📈 Prediction Result</h3>
                    </div>
                    <div className="card-body">
                        {/* Score Gauge */}
                        <div className="gauge-container">
                            <div className="gauge">
                                <div className="gauge-bg"></div>
                                <div className="gauge-fill" style={{
                                    transform: `rotate(${getGaugeRotation(result.readiness_score)}deg)`,
                                    background: result.category_color || '#7c6cff'
                                }}></div>
                                <div className="gauge-center">
                                    <div className="gauge-score">{result.readiness_score}</div>
                                    <div className="gauge-label">out of 100</div>
                                </div>
                            </div>
                            <div className="gauge-category" style={{ color: result.category_color }}>
                                {result.category}
                            </div>
                            <div className="gauge-probability">
                                Placement Probability: {(result.placement_probability * 100).toFixed(1)}%
                            </div>
                        </div>

                        {/* Feature Contributions */}
                        {result.contributions && (
                            <div className="contributions-section">
                                <h4>Feature Contributions</h4>
                                <div className="contributions-list">
                                    {Object.entries(result.contributions)
                                        .sort((a, b) => Math.abs(b[1].contribution) - Math.abs(a[1].contribution))
                                        .map(([key, info]) => (
                                            <div key={key} className="contrib-item">
                                                <div className="contrib-label">
                                                    <span>{info.label}</span>
                                                    <span className="contrib-val">{info.value}</span>
                                                </div>
                                                <div className="contrib-bar-wrapper">
                                                    <div className="contrib-bar"
                                                        style={{
                                                            width: `${Math.min(Math.abs(info.contribution) * 50, 100)}%`,
                                                            background: info.contribution >= 0
                                                                ? 'linear-gradient(90deg, #2ed573, #7bed9f)'
                                                                : 'linear-gradient(90deg, #ff4757, #ff6b81)',
                                                            marginLeft: info.contribution < 0 ? 'auto' : '50%',
                                                            marginRight: info.contribution >= 0 ? 'auto' : '50%',
                                                        }}
                                                    ></div>
                                                </div>
                                                <div className="contrib-impact" style={{
                                                    color: info.contribution >= 0 ? '#2ed573' : '#ff4757'
                                                }}>
                                                    {info.contribution >= 0 ? '+' : ''}{info.contribution.toFixed(3)}
                                                </div>
                                            </div>
                                        ))}
                                </div>
                            </div>
                        )}

                        {/* Category Legend */}
                        <div className="category-legend">
                            <div className="legend-item">
                                <span className="legend-dot" style={{ background: '#ff4757' }}></span>
                                <span>0–40: Not Ready</span>
                            </div>
                            <div className="legend-item">
                                <span className="legend-dot" style={{ background: '#ffa502' }}></span>
                                <span>40–70: Needs Preparation</span>
                            </div>
                            <div className="legend-item">
                                <span className="legend-dot" style={{ background: '#2ed573' }}></span>
                                <span>70–100: Placement Ready</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ReadinessScore;
