import axios from 'axios';

// Get API URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// User Registration
export const registerUser = async (userData: {
  username: string;
  email: string;
  attributes: Record<string, string>;
}) => {
  try {
    const response = await apiClient.post('/register', userData);
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

// Get User Info
export const getUser = async (bcid: string) => {
  try {
    const response = await apiClient.get(`/user/${bcid}`);
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

// Upload File
export const uploadFile = async (data: {
  file: File;
  bcid: string;
  accessPolicy: Record<string, string>;
  accessCode?: string;
}) => {
  try {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('bcid', data.bcid);
    formData.append('access_policy', JSON.stringify(data.accessPolicy));

    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

// Download File
export const downloadFile = async (cid: string, bcid: string) => {
  try {
    const response = await apiClient.post(
      `/download/${cid}`,
      { bcid },
      { responseType: 'blob' }
    );
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

// List User Files
export const listUserFiles = async (bcid: string) => {
  try {
    const response = await apiClient.get(`/files/${bcid}`);
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

// Get File Metadata
export const getFileMetadata = async (cid: string) => {
  try {
    const response = await apiClient.get(`/file/${cid}`);
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

// Get Access Logs
export const getAccessLogs = async (cid: string) => {
  try {
    const response = await apiClient.get(`/logs/${cid}`);
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

// Get Statistics
export const getStatistics = async () => {
  try {
    const response = await apiClient.get('/stats');
    return response.data;
  } catch (error: any) {
    throw error.response?.data || error.message;
  }
};

export default apiClient;