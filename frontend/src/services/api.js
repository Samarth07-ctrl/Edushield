/**
 * API Service for Federated Learning Frontend
 * Handles all communication with the backend server
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

/**
 * Health check
 */
export const healthCheck = async () => {
    const response = await api.get('/health');
    return response.data;
};

/**
 * Register a client
 */
export const registerClient = async (clientId) => {
    const response = await api.post('/register-client', { client_id: clientId });
    return response.data;
};

/**
 * Start federated training
 */
export const startTraining = async (useCase, numRounds) => {
    const response = await api.post('/federated/start', {
        use_case: useCase,
        num_rounds: numRounds
    });
    return response.data;
};

/**
 * Get training status
 */
export const getTrainingStatus = async () => {
    const response = await api.get('/federated/status');
    return response.data;
};

/**
 * Get training metrics
 */
export const getMetrics = async () => {
    const response = await api.get('/metrics');
    return response.data;
};

/**
 * Train centralized model
 */
export const trainCentralized = async (useCase, numClients = 5) => {
    const response = await api.post('/centralized/train', {
        use_case: useCase,
        num_clients: numClients
    });
    return response.data;
};

/**
 * Get comparison results
 */
export const getComparison = async () => {
    const response = await api.get('/comparison');
    return response.data;
};

/**
 * Get registered clients
 */
export const getClients = async () => {
    const response = await api.get('/clients');
    return response.data;
};

/**
 * Get available job roles
 */
export const getRoles = async () => {
    const response = await api.get('/roles');
    return response.data;
};

/**
 * Analyze skill gap for a target role
 */
export const analyzeSkillGap = async (studentSkills, targetRole) => {
    const response = await api.post('/skill-gap', {
        student_skills: studentSkills,
        target_role: targetRole
    });
    return response.data;
};

/**
 * Get interview readiness score
 */
export const getReadinessScore = async (profile) => {
    const response = await api.post('/readiness-score', profile);
    return response.data;
};

/**
 * Get SHAP explanation for readiness prediction
 */
export const explainReadiness = async (profile) => {
    const response = await api.post('/explain-readiness', profile);
    return response.data;
};

export default api;
