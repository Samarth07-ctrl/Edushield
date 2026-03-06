import React, { useState, useEffect } from 'react';
import { getClients } from '../services/api';

function ClientSimulator() {
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchClients();
        const interval = setInterval(fetchClients, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchClients = async () => {
        try {
            const data = await getClients();
            setClients(data.clients || []);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching clients:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p style={{ color: 'var(--text-muted)' }}>Loading clients...</p>
                </div>
            </div>
        );
    }

    return (
        <>
            <div className="card">
                <div className="card-header">
                    <h3>💻 Connected Client Nodes</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        Each client represents a student device with local data
                    </p>
                </div>

                <div className="card-grid">
                    <div className="stat-card">
                        <div className="stat-label">Total Clients</div>
                        <div className="stat-value">{clients.length}</div>
                        <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                            Active nodes
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-label">Privacy Status</div>
                        <div className="stat-value" style={{ fontSize: '1.5rem' }}>
                            <span className="status-badge active">
                                <span className="status-dot"></span>
                                Protected
                            </span>
                        </div>
                        <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                            Differential Privacy Enabled
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-label">Data Location</div>
                        <div className="stat-value" style={{ fontSize: '1.2rem' }}>
                            🏠 Local
                        </div>
                        <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                            Never leaves device
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-label">Encryption</div>
                        <div className="stat-value" style={{ fontSize: '1.2rem' }}>
                            🔐 AES-256
                        </div>
                        <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
                            Weight transmission
                        </div>
                    </div>
                </div>

                {clients.length > 0 ? (
                    <div className="client-list" style={{ marginTop: '1.5rem' }}>
                        {clients.map((clientId) => (
                            <div key={clientId} className="client-item">
                                <div className="client-info">
                                    <div className="client-avatar">
                                        {clientId}
                                    </div>
                                    <div>
                                        <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                                            Client Node {clientId}
                                        </div>
                                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                            Local training enabled • Privacy protected
                                        </div>
                                    </div>
                                </div>
                                <div className="status-badge active">
                                    <span className="status-dot"></span>
                                    Connected
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="alert alert-info" style={{ marginTop: '1.5rem' }}>
                        No clients connected yet. Start client nodes to see them here.
                    </div>
                )}
            </div>

            <div className="card">
                <div className="card-header">
                    <h3>🔒 Privacy Features</h3>
                </div>

                <div style={{ display: 'grid', gap: '1rem' }}>
                    <div style={{
                        padding: '1rem',
                        background: 'var(--bg-tertiary)',
                        borderRadius: 'var(--radius-md)',
                        borderLeft: '4px solid var(--success)'
                    }}>
                        <h4 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span>✅</span> Differential Privacy
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Gaussian noise is added to model updates before transmission, ensuring individual
                            student data cannot be reverse-engineered from the shared weights.
                        </p>
                    </div>

                    <div style={{
                        padding: '1rem',
                        background: 'var(--bg-tertiary)',
                        borderRadius: 'var(--radius-md)',
                        borderLeft: '4px solid var(--success)'
                    }}>
                        <h4 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span>✅</span> Local Training Only
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            All student data remains on the local device. Only model weights (not data)
                            are shared with the central server during aggregation.
                        </p>
                    </div>

                    <div style={{
                        padding: '1rem',
                        background: 'var(--bg-tertiary)',
                        borderRadius: 'var(--radius-md)',
                        borderLeft: '4px solid var(--success)'
                    }}>
                        <h4 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span>✅</span> Encrypted Communication
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            Model weights are encrypted using AES-256 before transmission over the network,
                            preventing interception and unauthorized access.
                        </p>
                    </div>

                    <div style={{
                        padding: '1rem',
                        background: 'var(--bg-tertiary)',
                        borderRadius: 'var(--radius-md)',
                        borderLeft: '4px solid var(--success)'
                    }}>
                        <h4 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span>✅</span> Secure Aggregation
                        </h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            The FedAvg algorithm aggregates encrypted weights from multiple clients without
                            ever accessing individual student records or raw training data.
                        </p>
                    </div>
                </div>
            </div>

            <div className="card">
                <div className="card-header">
                    <h3>📖 How to Start Clients</h3>
                </div>

                <div style={{ background: 'var(--bg-tertiary)', padding: '1rem', borderRadius: 'var(--radius-md)', fontFamily: 'monospace' }}>
                    <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                        Open separate terminals and run:
                    </p>
                    <div style={{ background: 'var(--bg-primary)', padding: '1rem', borderRadius: 'var(--radius-sm)', marginBottom: '0.5rem' }}>
                        <code style={{ color: 'var(--success)' }}>python client.py --client-id 1 --server-url http://localhost:5000</code>
                    </div>
                    <div style={{ background: 'var(--bg-primary)', padding: '1rem', borderRadius: 'var(--radius-sm)', marginBottom: '0.5rem' }}>
                        <code style={{ color: 'var(--success)' }}>python client.py --client-id 2 --server-url http://localhost:5000</code>
                    </div>
                    <div style={{ background: 'var(--bg-primary)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                        <code style={{ color: 'var(--success)' }}>python client.py --client-id 3 --server-url http://localhost:5000</code>
                    </div>
                </div>
            </div>
        </>
    );
}

export default ClientSimulator;
