/**
 * Student Data API Service
 * Communicates with the Client Prediction API (port 5002)
 * All data stays local — predictions computed on the client side
 */

import axios from 'axios';

const STUDENT_API_URL = 'http://localhost:5002';

const studentApi = axios.create({
    baseURL: STUDENT_API_URL,
    timeout: 15000,
    headers: { 'Content-Type': 'application/json' }
});

export const getAttendance = async (clientId, studentId) => {
    const response = await studentApi.get('/api/student/attendance', {
        params: { client_id: clientId, student_id: studentId }
    });
    return response.data;
};

export const getMarks = async (clientId, studentId) => {
    const response = await studentApi.get('/api/student/marks', {
        params: { client_id: clientId, student_id: studentId }
    });
    return response.data;
};

export const predictRisk = async (clientId, studentId) => {
    const response = await studentApi.get('/predict-risk', {
        params: { client_id: clientId, student_id: studentId }
    });
    return response.data;
};

export const getPlacementReadiness = async (clientId, studentId) => {
    const response = await studentApi.get('/placement-readiness', {
        params: { client_id: clientId, student_id: studentId }
    });
    return response.data;
};

export const getStudyPlan = async (clientId, studentId) => {
    const response = await studentApi.get('/api/student/study-plan', {
        params: { client_id: clientId, student_id: studentId }
    });
    return response.data;
};

export const getStudentIds = async (clientId) => {
    const response = await studentApi.get('/api/student/ids', {
        params: { client_id: clientId }
    });
    return response.data;
};

export const studentHealthCheck = async () => {
    const response = await studentApi.get('/health');
    return response.data;
};

export default studentApi;
