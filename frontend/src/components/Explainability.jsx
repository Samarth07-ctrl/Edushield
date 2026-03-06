import React, { useState } from 'react';
import { explainReadiness } from '../services/api';

function Explainability() {
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
        { key: 'gpa', label: 'GPA', min: 0, max: 10, step: 0.1 },
        { key: 'dsa_score', label: 'DSA Score', min: 0, max: 100, step: 1 },
        { key: 'projects', label: 'Projects', min: 0, max: 15, step: 1 },
        { key: 'internships', label: 'Internships', min: 0, max: 5, step: 1 },
        { key: 'communication_score', label: 'Communication', min: 0, max: 100, step: 1 },
        { key: 'coding_score', label: 'Coding', min: 0, max: 100, step: 1 },
    ];

    const handleChange = (key, value) => {
        setProfile(prev => ({ ...prev, [key]: parseFloat(value) || 0 }));
    };

    const handleExplain = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await explainReadiness(profile);
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.error || 'Explanation failed');
        } finally {
            setLoading(false);
        }
    };

    const maxAbsImpact = result ? Math.max(
        ...Object.values(result.shap_values || {}).map(v => Math.abs(v.impact)),
        0.01
    ) : 1;

    return (
        <div className="career-section">
            <div className="career-card">
                <div className="card-header">
                    <h3>🔬 Explainable AI (SHAP)</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                        Understand WHY the model made its prediction
                    </p>
                </div>
                <div className="card-body">
                    <div className="profile-inputs compact">
                        {fields.map(f => (
                            <div key={f.key} className="input-group">
                                <label>{f.label}</label>
                                <input
                                    type="number"
                                    min={f.min}
                                    max={f.max}
                                    step={f.step}
                                    value={profile[f.key]}
                                    onChange={(e) => handleChange(f.key, e.target.value)}
                                    className="career-input"
                                />
                            </div>
                        ))}
                    </div>

                    <button
                        onClick={handleExplain}
                        disabled={loading}
                        className="btn btn-primary career-btn"
                    >
                        {loading ? '⏳ Computing SHAP values...' : '🔬 Explain Prediction'}
                    </button>

                    {error && <div className="career-error">{error}</div>}
                </div>
            </div>

            {result && (
                <>
                    {/* Summary Card */}
                    <div className="career-card">
                        <div className="card-header">
                            <h3>📝 Explanation Summary</h3>
                            <div className="readiness-badge" style={{
                                background: result.readiness_score >= 70 ? '#2ed573' :
                                    result.readiness_score >= 40 ? '#ffa502' : '#ff4757'
                            }}>
                                Score: {result.readiness_score}%
                            </div>
                        </div>
                        <div className="card-body">
                            <p className="explanation-summary">{result.explanation_summary}</p>
                            <div className="method-badge">
                                Method: {result.method === 'shap' ? '🔬 SHAP (Shapley Values)' : '📊 Coefficient-Based'}
                            </div>
                        </div>
                    </div>

                    {/* SHAP Waterfall Chart */}
                    <div className="career-card">
                        <div className="card-header">
                            <h3>📊 Feature Importance (SHAP Values)</h3>
                        </div>
                        <div className="card-body">
                            <div className="shap-chart">
                                {Object.entries(result.shap_values || {})
                                    .sort((a, b) => Math.abs(b[1].impact) - Math.abs(a[1].impact))
                                    .map(([key, info]) => (
                                        <div key={key} className="shap-row">
                                            <div className="shap-label">
                                                <span className="shap-feature">{info.label}</span>
                                                <span className="shap-value">= {info.value}</span>
                                            </div>
                                            <div className="shap-bar-container">
                                                <div className="shap-bar-track">
                                                    <div className="shap-center-line"></div>
                                                    <div
                                                        className="shap-bar"
                                                        style={{
                                                            width: `${(Math.abs(info.impact) / maxAbsImpact) * 45}%`,
                                                            background: info.impact >= 0
                                                                ? 'linear-gradient(90deg, #2ed573aa, #2ed573)'
                                                                : 'linear-gradient(270deg, #ff4757aa, #ff4757)',
                                                            left: info.impact >= 0 ? '50%' : 'auto',
                                                            right: info.impact < 0 ? '50%' : 'auto',
                                                        }}
                                                    ></div>
                                                </div>
                                            </div>
                                            <div className="shap-impact" style={{
                                                color: info.impact >= 0 ? '#2ed573' : '#ff4757'
                                            }}>
                                                {info.impact >= 0 ? '+' : ''}{info.impact.toFixed(4)}
                                            </div>
                                        </div>
                                    ))}
                            </div>
                        </div>
                    </div>

                    {/* Positive / Negative Factors */}
                    <div className="factors-grid">
                        <div className="career-card factor-card positive">
                            <div className="card-header">
                                <h3>✅ Positive Factors</h3>
                            </div>
                            <div className="card-body">
                                {result.positive_factors?.length > 0 ? (
                                    result.positive_factors.map((f, i) => (
                                        <div key={i} className="factor-item">
                                            <span className="factor-name">{f.label}</span>
                                            <span className="factor-val" style={{ color: '#2ed573' }}>
                                                +{f.impact.toFixed(4)}
                                            </span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="empty-text">No significant positive factors</p>
                                )}
                            </div>
                        </div>

                        <div className="career-card factor-card negative">
                            <div className="card-header">
                                <h3>⚠️ Negative Factors</h3>
                            </div>
                            <div className="card-body">
                                {result.negative_factors?.length > 0 ? (
                                    result.negative_factors.map((f, i) => (
                                        <div key={i} className="factor-item">
                                            <span className="factor-name">{f.label}</span>
                                            <span className="factor-val" style={{ color: '#ff4757' }}>
                                                {f.impact.toFixed(4)}
                                            </span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="empty-text">No significant negative factors</p>
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

export default Explainability;
