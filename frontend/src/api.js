import axios from 'axios';

/**
 * Centralized API configuration for Pickr.
 * Uses VITE_API_URL environment variable if available, 
 * otherwise defaults to localhost.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 second timeout for large uploads
});

// Response interceptor for consistent error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        let message = 'An unexpected error occurred';

        if (error.response) {
            // Server responded with a status code outside the 2xx range
            message = error.response.data?.detail || `Server error: ${error.response.status}`;
        } else if (error.request) {
            // Request was made but no response was received
            message = 'Could not connect to the backend server. Is it running?';
        } else {
            // Something happened in setting up the request
            message = error.message;
        }

        return Promise.reject(new Error(message));
    }
);

export default api;
