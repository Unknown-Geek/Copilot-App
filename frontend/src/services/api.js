
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