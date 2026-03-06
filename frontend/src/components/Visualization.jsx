import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getMetrics } from '../services/api';

function Visualization() {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchMetrics = async () => {
        try {
            const data = await getMetrics();
            setMetrics(data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching metrics:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p style={{ color: 'var(--text-muted)' }}>Loading metrics...</p>
                </div>
            </div>
        );
    }

    if (!metrics || metrics.rounds.length === 0) {
        return (
            <div className="card">
                <div className="alert alert-info">
                    No training data available yet. Start a training session to see metrics.
                </div>
            </div>
        );
    }

    // Prepare data for charts
    const chartData = metrics.rounds.map((round, index) => ({
        round,
        accuracy: (metrics.accuracy[index] * 100).toFixed(2),
        loss: metrics.loss[index].toFixed(4),
        privacy_budget: metrics.privacy_budget[index].toFixed(2),
        clients: metrics.num_clients[index]
    }));

    return (
        <>
            <div className="card-grid">
                <div className="stat-card">
                    <div className="stat-label">Final Accuracy</div>
                    <div className="stat-value">
                        {(metrics.accuracy[metrics.accuracy.length - 1] * 100).toFixed(1)}%
                    </div>
                    <div className="stat-change positive">
                        ↑ {((metrics.accuracy[metrics.accuracy.length - 1] - metrics.accuracy[0]) * 100).toFixed(1)}% improvement
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-label">Final Loss</div>
                    <div className="stat-value">
                        {metrics.loss[metrics.loss.length - 1].toFixed(4)}
                    </div>
                    <div className="stat-change positive">
                        ↓ {((metrics.loss[0] - metrics.loss[metrics.loss.length - 1]) / metrics.loss[0] * 100).toFixed(1)}% reduction
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-label">Privacy Budget (ε)</div>
                    <div className="stat-value">
                        {metrics.privacy_budget[metrics.privacy_budget.length - 1].toFixed(2)}
                    </div>
                    <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                        Lower is more private
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-label">Total Rounds</div>
                    <div className="stat-value">
                        {metrics.rounds.length}
                    </div>
                    <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                        Completed
                    </div>
                </div>
            </div>

            <div className="chart-container">
                <h3 style={{ marginBottom: '1.5rem' }}>📈 Accuracy Over Rounds</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis
                            dataKey="round"
                            stroke="var(--text-muted)"
                            label={{ value: 'Round', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
                        />
                        <YAxis
                            stroke="var(--text-muted)"
                            label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border)',
                                borderRadius: 'var(--radius-md)',
                                color: 'var(--text-primary)'
                            }}
                        />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="accuracy"
                            stroke="#10b981"
                            strokeWidth={3}
                            dot={{ fill: '#10b981', r: 4 }}
                            name="Accuracy (%)"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="chart-container">
                <h3 style={{ marginBottom: '1.5rem' }}>📉 Loss Over Rounds</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis
                            dataKey="round"
                            stroke="var(--text-muted)"
                            label={{ value: 'Round', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
                        />
                        <YAxis
                            stroke="var(--text-muted)"
                            label={{ value: 'Loss', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border)',
                                borderRadius: 'var(--radius-md)',
                                color: 'var(--text-primary)'
                            }}
                        />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="loss"
                            stroke="#ef4444"
                            strokeWidth={3}
                            dot={{ fill: '#ef4444', r: 4 }}
                            name="Loss"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="chart-container">
                <h3 style={{ marginBottom: '1.5rem' }}>👥 Client Participation</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis
                            dataKey="round"
                            stroke="var(--text-muted)"
                            label={{ value: 'Round', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
                        />
                        <YAxis
                            stroke="var(--text-muted)"
                            label={{ value: 'Clients', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border)',
                                borderRadius: 'var(--radius-md)',
                                color: 'var(--text-primary)'
                            }}
                        />
                        <Legend />
                        <Bar
                            dataKey="clients"
                            fill="#6366f1"
                            name="Active Clients"
                            radius={[8, 8, 0, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            <div className="chart-container">
                <h3 style={{ marginBottom: '1.5rem' }}>🔒 Privacy Budget Consumption</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis
                            dataKey="round"
                            stroke="var(--text-muted)"
                            label={{ value: 'Round', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
                        />
                        <YAxis
                            stroke="var(--text-muted)"
                            label={{ value: 'Epsilon (ε)', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
                        />
                        <Tooltip
                            contentStyle={{
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border)',
                                borderRadius: 'var(--radius-md)',
                                color: 'var(--text-primary)'
                            }}
                        />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="privacy_budget"
                            stroke="#f59e0b"
                            strokeWidth={3}
                            dot={{ fill: '#f59e0b', r: 4 }}
                            name="Privacy Budget (ε)"
                        />
                    </LineChart>
                </ResponsiveContainer>
                <div className="alert alert-info" style={{ marginTop: '1rem' }}>
                    <strong>Privacy Note:</strong> Lower epsilon (ε) values indicate stronger privacy guarantees.
                    The system uses differential privacy to protect individual student data.
                </div>
            </div>
        </>
    );
}

export default Visualization;
