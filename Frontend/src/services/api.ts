import axios, { AxiosError } from 'axios';
import { UOAResponse, ErrorResponse } from '../types/api';

// Auto-detect environment and set appropriate API URL
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://uoa-options-scanner.vercel.app'  // Production Vercel URL
  : 'http://localhost:8000';  // Local development

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for options data fetching
  headers: {
    'Content-Type': 'application/json',
  },
});

export class ApiError extends Error {
  constructor(message: string, public statusCode?: number, public ticker?: string) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Fetch unusual options activity data for a given ticker
 */
export const fetchUoaData = async (ticker: string, mode: string = 'auto'): Promise<UOAResponse> => {
  try {
    const response = await api.get<UOAResponse>(`/api/analyze/${ticker.toUpperCase()}?mode=${mode}`);
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.response?.data) {
        const errorData = error.response.data as ErrorResponse;
        throw new ApiError(
          errorData.detail || 'An error occurred while fetching data',
          error.response.status,
          ticker
        );
      } else if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR') {
        throw new ApiError('Unable to connect to the server. Please make sure the backend is running.');
      } else if (error.code === 'ECONNABORTED') {
        throw new ApiError('Request timeout. The analysis is taking too long - please try again.');
      }
    }
    
    throw new ApiError('An unexpected error occurred while fetching data');
  }
};

/**
 * Check if the API server is available
 */
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    await api.get('/');
    return true;
  } catch {
    return false;
  }
};

