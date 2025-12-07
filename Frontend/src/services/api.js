const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  /**
   * Get authentication token from localStorage
   */
  getAuthToken() {
    return localStorage.getItem('token');
  }

  /**
   * Get authentication headers
   */
  getAuthHeaders() {
    const token = this.getAuthToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  /**
   * Analyze symptoms and get probable conditions
   * @param {string} symptoms - User input symptoms
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeSymptoms(symptoms) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/symptoms/analyze`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ symptoms }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to analyze symptoms');
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing symptoms:', error);
      throw error;
    }
  }

  /**
   * Get query history
   * @param {string|null} userId - Optional user identifier
   * @param {number} limit - Maximum number of queries
   * @returns {Promise<Array>} List of queries
   */
  async getHistory(userId = null, limit = 10) {
    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      if (userId) {
        params.append('user_id', userId);
      }

      const response = await fetch(`${API_BASE_URL}/api/symptoms/history?${params}`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch history');
      }

      const data = await response.json();
      return data.queries || [];
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  }

  /**
   * Get a specific query by ID
   * @param {string} queryId - Query document ID
   * @returns {Promise<Object>} Query document
   */
  async getQuery(queryId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/symptoms/query/${queryId}`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch query');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching query:', error);
      throw error;
    }
  }

  /**
   * Analyze symptoms from an image
   * @param {File} imageFile - Image file to analyze
   * @param {string|null} symptoms - Optional text description
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeImage(imageFile, symptoms = null) {
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      if (symptoms) {
        formData.append('symptoms', symptoms);
      }

      const token = this.getAuthToken();
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/symptoms/analyze-image`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to analyze image');
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing image:', error);
      throw error;
    }
  }

  /**
   * Upload PDF for RAG processing
   * @param {File} pdfFile - PDF file to upload
   * @returns {Promise<Object>} Upload result
   */
  async uploadPDF(pdfFile) {
    try {
      const formData = new FormData();
      formData.append('pdf', pdfFile);

      const token = this.getAuthToken();
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/api/symptoms/upload-pdf`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload PDF');
      }

      return await response.json();
    } catch (error) {
      console.error('Error uploading PDF:', error);
      throw error;
    }
  }

  /**
   * Analyze symptoms using PDF RAG
   * @param {string} symptoms - User input symptoms
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeWithPDF(symptoms) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/symptoms/analyze-with-pdf`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          symptoms,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to analyze with PDF');
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing with PDF:', error);
      throw error;
    }
  }
}

class AuthService {
  /**
   * Register a new user
   */
  async register(email, password, fullName) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName })
    });

    if (!response.ok) {
      throw response;
    }

    return await response.json();
  }

  /**
   * Login with email and password
   */
  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 uses 'username' field
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    if (!response.ok) {
      throw response;
    }

    return await response.json();
  }

  /**
   * Get current user info
   */
  async getCurrentUser() {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw response;
    }

    return await response.json();
  }

  /**
   * Get user symptom history
   */
  async getHistory(limit = 20) {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No token found');
    }

    const response = await fetch(`${API_BASE_URL}/auth/history?limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw response;
    }

    return await response.json();
  }

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem('token');
  }
}

export const authAPI = new AuthService();
export default new ApiService();

