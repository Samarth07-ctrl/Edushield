import React, { useState, useEffect } from 'react';
import { startTraining, getTrainingStatus } from '../services/api';

function TrainingControl() {
    const [useCase, setUseCase] = useState('attendance');
    const [numRounds, setNumRounds] = useState(10);
    const [isTraining, setIsTraining] = useState(false);
    const [status, setStatus] = useState(null);
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 3000);
        return () => clearInterval(interval);
    }, []);

    const fetchStatus = async () => {
        try {
            const data = await getTrainingStatus();
            setStatus(data);
            setIsTraining(data.active);
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    };

    const handleStartTraining = async () => {
        try {
            setMessage('');
            const response = await startTraining(useCase, numRounds);
            setMessage(`Training started: ${response.message}`);
            setIsTraining(true);
        } catch (error) {
            setMessage(`Error: ${error.response?.data?.error || error.message}`);
        }
    };

    const progress = status ? (status.current_round / status.total_rounds) * 100 : 0;

    return (
        <div className="card">
            <div className="card-header">
                <h3>🎯 Training Control Panel</h3>
            </div>

            {message && (
                <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
                    {message}
                </div>
            )}

            <div className="control-group">
                <div className="form-group">
                    <label>Use Case</label>
                    <select
                        className="select-input"
                        value={useCase}
                        onChange={(e) => setUseCase(e.target.value)}
                        disabled={isTraining}
                    >
                        <option value="attendance">Attendance Risk Prediction</option>
                        <option value="learning">Learning Recommendation</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Number of Rounds</label>
                    <input
                        type="number"
                        className="form-input"
                        value={numRounds}
                        onChange={(e) => setNumRounds(parseInt(e.target.value))}
                        min="1"
                        max="50"
                        disabled={isTraining}
                    />
                </div>

                <div className="form-group">
                    <label style={{ opacity: 0 }}>Action</label>
                    <button
                        className="btn btn-success"
                        onClick={handleStartTraining}
                        disabled={isTraining}
                        style={{ width: '100%' }}
                    >
                        {isTraining ? '⏸️ Training...' : '▶️ Start Training'}
                    </button>
                </div>
            </div>

            {status && (
                <>
                    <div className="card-grid" style={{ marginTop: '1.5rem' }}>
                        <div className="stat-card">
                            <div className="stat-label">Current Round</div>
                            <div className="stat-value">{status.current_round} / {status.total_rounds}</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-label">Connected Clients</div>
                            <div className="stat-value">{status.registered_clients}</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-label">Status</div>
                            <div className="stat-value" style={{ fontSize: '1.5rem' }}>
                                <span className={`status-badge ${status.active ? 'training' : 'inactive'}`}>
                                    <span className="status-dot"></span>
                                    {status.active ? 'Training' : 'Idle'}
                                </span>
                            </div>
                        </div>

                        {status.latest_metrics && (
                            <div className="stat-card">
                                <div className="stat-label">Latest Accuracy</div>
                                <div className="stat-value">
                                    {(status.latest_metrics.accuracy * 100).toFixed(1)}%
                                </div>
                            </div>
                        )}
                    </div>

                    {isTraining && (
                        <div style={{ marginTop: '1.5rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                    Training Progress
                                </span>
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                    {progress.toFixed(0)}%
                                </span>
                            </div>
                            <div className="progress-bar">
                                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default TrainingControl;
