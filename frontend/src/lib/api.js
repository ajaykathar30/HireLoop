import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Required for cookie-based JWT
});

export const authApi = {
  signupCandidate: (data) => api.post('/auth/signup/candidate', data),
  signupCompany: (data) => api.post('/auth/signup/company', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
};

export const candidateApi = {
  updateProfile: (data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    return api.patch('/candidates/update', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

export const companyApi = {
  updateProfile: (data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    return api.patch('/companies/update', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

export const jobApi = {
  create: (data) => api.post('/jobs', data),
  getCompanyJobs: () => api.get('/jobs/my-jobs'),
  getAllJobs: () => api.get('/jobs'),
  triggerPipeline: (jobId) => api.post(`/jobs/${jobId}/trigger-pipeline`),
};

export const applicationApi = {
  apply: (data) => api.post('/applications', data),
  getMyApplications: () => api.get('/applications/my-applications'),
  getJobApplications: (jobId) => api.get(`/applications/job/${jobId}`),
};

export const interviewApi = {
  getMySessions: () => api.get('/interviews/my-sessions'),
  start: (sessionId) => api.post(`/interviews/${sessionId}/start`),
  submitAnswer: (sessionId, audioBlob, isTimeout, forceFinalize = false) => {
    const formData = new FormData();
    if (audioBlob) {
      formData.append('audio_file', audioBlob, 'answer.wav');
    }
    formData.append('is_timeout', isTimeout);
    formData.append('force_finalize', forceFinalize);
    
    return api.post(`/interviews/${sessionId}/submit-answer`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getDetails: (sessionId) => api.get(`/interviews/${sessionId}`),
  getSessionByAppId: (appId) => api.get(`/interviews/session/${appId}`),
  getJobReports: (jobId) => api.get(`/interviews/job/${jobId}/reports`),
};

export default api;
