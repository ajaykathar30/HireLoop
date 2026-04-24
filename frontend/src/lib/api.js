import axios from 'axios';

const API_URL = 'http://localhost:8000';

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
  getAllJobs: () => api.get('/jobs/'),
};

export const applicationApi = {
  apply: (data) => api.post('/applications/', data),
};

export default api;
