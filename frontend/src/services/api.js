import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const generateDocumentation = async (codebase) => {
  const response = await axios.post(`${API_BASE_URL}/documentation`, codebase);
  return response.data;
};

export const getDocumentation = async (projectId) => {
  const response = await axios.get(`${API_BASE_URL}/documentation/${projectId}`);
  return response.data;
};

export const loginUser = async (credentials) => {
  const response = await axios.post(`${API_BASE_URL}/auth/login`, credentials);
  return response.data;
};

export const exportDocumentation = async (projectId, format) => {
  const response = await axios.get(`${API_BASE_URL}/documentation/${projectId}/export/${format}`);
  return response.data;
};

export const updateDocumentationSettings = async (projectId, settings) => {
  const response = await axios.put(`${API_BASE_URL}/documentation/${projectId}/settings`, settings);
  return response.data;
};