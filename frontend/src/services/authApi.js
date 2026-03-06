/**
 * Authentication API Service
 * Communicates with the auth server (port 5001)
 */

import axios from 'axios';

const AUTH_API_URL = 'http://localhost:5001';

const authApi = axios.create({
    baseURL: AUTH_API_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
});

// Attach JWT token to every request
authApi.interceptors.request.use((config) => {
    const token = localStorage.getItem('student_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const registerStudent = async (data) => {
    const response = await authApi.post('/auth/register', data);
    return response.data;
};

export const loginStudent = async (email, password) => {
    const response = await authApi.post('/auth/login', { email, password });
    return response.data;
};

export const getMe = async () => {
    const response = await authApi.get('/auth/me');
    return response.data;
};

export const authHealthCheck = async () => {
    const response = await authApi.get('/auth/health');
    return response.data;
};

export default authApi;
