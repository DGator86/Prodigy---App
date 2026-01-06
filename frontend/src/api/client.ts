import axios from 'axios';

// API base URL - relative path works with nginx proxy
const API_BASE_URL = '/api/v1';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: async (data: {
    email: string;
    password: string;
    name: string;
    height_in?: number;
    weight_lb?: number;
  }) => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  getMe: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// Workouts API
export const workoutsApi = {
  create: async (data: any) => {
    const response = await apiClient.post('/workouts', data);
    return response.data;
  },

  list: async (params?: {
    page?: number;
    limit?: number;
    workout_type?: string;
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await apiClient.get('/workouts', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await apiClient.get(`/workouts/${id}`);
    return response.data;
  },

  delete: async (id: string) => {
    await apiClient.delete(`/workouts/${id}`);
  },
};

// Domains API
export const domainsApi = {
  getAll: async () => {
    const response = await apiClient.get('/domains');
    return response.data;
  },

  getRadar: async () => {
    const response = await apiClient.get('/domains/radar');
    return response.data;
  },

  getDetail: async (domain: string) => {
    const response = await apiClient.get(`/domains/${domain}`);
    return response.data;
  },

  getTrends: async (period: '7d' | '30d' | '90d' = '30d') => {
    const response = await apiClient.get('/domains/trends', { params: { period } });
    return response.data;
  },
};

// Export API
export const exportApi = {
  csv: async (params?: { start_date?: string; end_date?: string }) => {
    const response = await apiClient.get('/export/csv', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },

  json: async (params?: {
    start_date?: string;
    end_date?: string;
    include_distributions?: boolean;
  }) => {
    const response = await apiClient.get('/export/json', { params });
    return response.data;
  },
};
