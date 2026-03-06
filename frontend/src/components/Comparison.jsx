import React, { useState, useEffect } from 'react';
import { trainCentralized, getComparison } from '../services/api';

function Comparison() {
    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(false);
    const [training, setTraining] = useState(false);
    const [message, setMessage] = useState('');
    const [useCase, setUseCase] = useState('attendance');

    useEffect(() => {
        fetchComparison();
    }, []);

    const fetchComparison = async () => {
        try {
            const data = await getComparison();
            setComparison(data);
        } catch (error) {
            // Comparison not available yet
            console.log('Comparison not available');
        }
    };

    const handleTrainCentralized = async () => {
        try {
            setMessage('');
            setTraining(true);
            const response = await trainCentralized(useCase, 5);
            setMessage(`Centralized training completed: ${response.message}`);

            // Fetch comparison after training
            setTimeout(fetchComparison, 1000);
        } catch (error) {
            setMessage(`Error: ${error.response?.data?.error || error.message}`);
        } finally {
            setTraining(false);
        }
    };

    return (
        <>
            <div className="card">
                <div className="card-header">
                    <h3>⚖️ Centralized vs Federated Comparison</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        Compare privacy-preserving federated learning with traditional centralized approach
                    </p>
                </div>

                {message && (
                    <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
                        {message}
                    </div>
                )}

                <div className="control-group">
                    <div className="form-group">
                        <label>Use Case for Centralized Training</label>
                        <select
                            className="select-input"
                            value={useCase}
                            onChange={(e) => setUseCase(e.target.value)}
                            disabled={training}
                        >
                            <option value="attendance">Attendance Risk Prediction</option>
                            <option value="learning">Learning Recommendation</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label style={{ opacity: 0 }}>Action</label>
                        <button
                            className="btn btn-primary"
                            onClick={handleTrainCentralized}
                            disabled={training}
                            style={{ width: '100%' }}
                        >
                            {training ? '⏳ Training...' : '🚀 Train Centralized Model'}
                        </button>
                    </div>
                </div>

                {training && (
                    <div className="loading-container">
                        <div className="spinner"></div>
                        <p style={{ color: 'var(--text-muted)' }}>
                            Training centralized model... This may take a minute.
                        </p>
                    </div>
                )}
            </div>

            {comparison && (
                <>
                    <div className="card">
                        <div className="card-header">
                            <h3>📊 Performance Comparison</h3>
                        </div>

                        <table className="comparison-table">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Centralized</th>
                                    <th>Federated</th>
                                    <th>Winner</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Accuracy</strong></td>
                                    <td>{(comparison.centralized.accuracy * 100).toFixed(2)}%</td>
                                    <td>{(comparison.federated.accuracy * 100).toFixed(2)}%</td>
                                    <td>
                                        {comparison.winner.accuracy === 'centralized' ? (
                                            <span className="winner-badge">Centralized</span>
                                        ) : (
                                            <span className="winner-badge">Federated</span>
                                        )}
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Privacy Score</strong></td>
                                    <td>{comparison.centralized.privacy_score}%</td>
                                    <td>{comparison.federated.privacy_score}%</td>
                                    <td>
                                        <span className="winner-badge">Federated</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Communication Cost</strong></td>
                                    <td>{comparison.centralized.communication_cost} bytes</td>
                                    <td>{comparison.federated.communication_cost.toLocaleString()} bytes</td>
                                    <td>
                                        <span className="winner-badge">Centralized</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Training Time</strong></td>
                                    <td>{comparison.centralized.training_time.toFixed(2)}s</td>
                                    <td>-</td>
                                    <td>-</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div className="card-grid">
                        <div className="stat-card">
                            <div className="stat-label">Accuracy Difference</div>
                            <div className="stat-value" style={{
                                color: comparison.differences.accuracy_diff >= 0 ? 'var(--success)' : 'var(--danger)'
                            }}>
                                {comparison.differences.accuracy_diff >= 0 ? '+' : ''}
                                {(comparison.differences.accuracy_diff * 100).toFixed(2)}%
                            </div>
                            <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                                Federated vs Centralized
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-label">Privacy Gain</div>
                            <div className="stat-value" style={{ color: 'var(--success)' }}>
                                +{comparison.differences.privacy_gain}%
                            </div>
                            <div className="stat-change positive">
                                Complete privacy preservation
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-label">Communication Overhead</div>
                            <div className="stat-value" style={{ fontSize: '1.2rem' }}>
                                {(comparison.differences.communication_overhead / 1024).toFixed(1)} KB
                            </div>
                            <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                                Additional network usage
                            </div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-label">Overall Winner</div>
                            <div className="stat-value" style={{ fontSize: '1.5rem' }}>
                                <span className="status-badge active">
                                    🏆 {comparison.winner.overall === 'federated' ? 'Federated' : 'Centralized'}
                                </span>
                            </div>
                            <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                                Best approach
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="card-header">
                            <h3>💡 Key Insights</h3>
                        </div>

                        <div style={{ display: 'grid', gap: '1rem' }}>
                            <div style={{
                                padding: '1rem',
                                background: 'var(--bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                borderLeft: '4px solid var(--primary)'
                            }}>
                                <h4 style={{ marginBottom: '0.5rem', color: 'var(--primary-light)' }}>
                                    🎯 Accuracy Trade-off
                                </h4>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                    Federated learning achieves comparable accuracy to centralized training while
                                    maintaining complete privacy. The slight accuracy difference (if any) is a
                                    worthwhile trade-off for privacy preservation.
                                </p>
                            </div>

                            <div style={{
                                padding: '1rem',
                                background: 'var(--bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                borderLeft: '4px solid var(--success)'
                            }}>
                                <h4 style={{ marginBottom: '0.5rem', color: 'var(--success)' }}>
                                    🔒 Privacy Advantage
                                </h4>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                    Federated learning provides 100% privacy protection as no student data ever
                                    leaves their device. Centralized approaches require collecting all data in
                                    one location, creating privacy risks and compliance challenges.
                                </p>
                            </div>

                            <div style={{
                                padding: '1rem',
                                background: 'var(--bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                borderLeft: '4px solid var(--warning)'
                            }}>
                                <h4 style={{ marginBottom: '0.5rem', color: 'var(--warning)' }}>
                                    📡 Communication Cost
                                </h4>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                    Federated learning requires multiple rounds of communication between clients
                                    and server, increasing network usage. However, this overhead is minimal compared
                                    to the privacy benefits gained.
                                </p>
                            </div>

                            <div style={{
                                padding: '1rem',
                                background: 'var(--bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                borderLeft: '4px solid var(--primary)'
                            }}>
                                <h4 style={{ marginBottom: '0.5rem', color: 'var(--primary-light)' }}>
                                    ⚡ Real-World Application
                                </h4>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                    For smart campus applications, federated learning enables collaborative model
                                    training across student devices while complying with data protection regulations
                                    like GDPR and FERPA. Students maintain full control of their data.
                                </p>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {!comparison && !training && (
                <div className="card">
                    <div className="alert alert-info">
                        <strong>Get Started:</strong> Train a centralized model and complete federated training
                        to see the comparison. Make sure you've run federated training first from the Dashboard tab.
                    </div>
                </div>
            )}
        </>
    );
}

export default Comparison;
