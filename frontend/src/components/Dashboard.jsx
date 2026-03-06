import React, { useState, useEffect } from 'react';
import TrainingControl from './TrainingControl';
import Visualization from './Visualization';
import ClientSimulator from './ClientSimulator';
import Comparison from './Comparison';
import SkillGap from './SkillGap';
import ReadinessScore from './ReadinessScore';
import Explainability from './Explainability';
import { healthCheck } from '../services/api';

function Dashboard({ onLogout }) {
    const [activeTab, setActiveTab] = useState('overview');
    const [serverStatus, setServerStatus] = useState('checking');

    useEffect(() => {
        checkServerHealth();
        const interval = setInterval(checkServerHealth, 10000);
        return () => clearInterval(interval);
    }, []);

    const checkServerHealth = async () => {
        try {
            await healthCheck();
            setServerStatus('online');
        } catch (error) {
            setServerStatus('offline');
        }
    };

    const renderContent = () => {
        switch (activeTab) {
            case 'overview':
                return (
                    <>
                        <TrainingControl />
                        <Visualization />
                    </>
                );
            case 'clients':
                return <ClientSimulator />;
            case 'comparison':
                return <Comparison />;
            case 'skill-gap':
                return <SkillGap />;
            case 'readiness':
                return <ReadinessScore />;
            case 'explainability':
                return <Explainability />;
            default:
                return <TrainingControl />;
        }
    };

    const tabTitle = {
        'overview': '📊 Training Dashboard',
        'clients': '💻 Client Management',
        'comparison': '⚖️ Model Comparison',
        'skill-gap': '🎯 Skill Gap Analysis',
        'readiness': '🏆 Interview Readiness',
        'explainability': '🔬 Explainable AI',
    };

    const tabSubtitle = {
        'overview': 'Monitor and control federated learning training',
        'clients': 'View and manage connected client nodes',
        'comparison': 'Compare centralized vs federated approaches',
        'skill-gap': 'Analyze skill gaps against target job roles',
        'readiness': 'ML-powered placement readiness prediction',
        'explainability': 'SHAP-based model explanation and interpretability',
    };

    return (
        <div className="dashboard">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <h2>🛡️ EduShield AI</h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        Privacy-Preserving ML
                    </p>
                </div>

                <nav className="sidebar-nav">
                    {/* Existing FL Tabs */}
                    <div className="nav-section-label">Federated Learning</div>
                    {[
                        { key: 'overview', icon: '📊', label: 'Dashboard' },
                        { key: 'clients', icon: '💻', label: 'Client Nodes' },
                        { key: 'comparison', icon: '⚖️', label: 'Comparison' },
                    ].map(tab => (
                        <div
                            key={tab.key}
                            className={`nav-item ${activeTab === tab.key ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.key)}
                        >
                            <span>{tab.icon}</span>
                            <span>{tab.label}</span>
                        </div>
                    ))}

                    {/* Career Readiness Tabs */}
                    <div className="nav-section-label" style={{ marginTop: '1rem' }}>Career Intelligence</div>
                    {[
                        { key: 'skill-gap', icon: '🎯', label: 'Skill Gap' },
                        { key: 'readiness', icon: '🏆', label: 'Readiness Score' },
                        { key: 'explainability', icon: '🔬', label: 'Explainable AI' },
                    ].map(tab => (
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
                    <div style={{ marginBottom: '1rem' }}>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                            Server Status
                        </div>
                        <div className={`status-badge ${serverStatus === 'online' ? 'active' : 'inactive'}`}>
                            <span className="status-dot"></span>
                            {serverStatus === 'online' ? 'Online' : 'Offline'}
                        </div>
                    </div>
                    <button onClick={onLogout} className="btn btn-secondary" style={{ width: '100%' }}>
                        Logout
                    </button>
                </div>
            </aside>

            <main className="main-content">
                <div className="content-header">
                    <div>
                        <h1>{tabTitle[activeTab]}</h1>
                        <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                            {tabSubtitle[activeTab]}
                        </p>
                    </div>
                </div>

                {renderContent()}
            </main>
        </div>
    );
}

export default Dashboard;
