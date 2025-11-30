/**
 * Common utilities for frontend pages
 */

// API Base URL - adjust based on environment
const API_BASE_URL = window.location.origin;

/**
 * Get the stored JWT token
 * @returns {string|null} JWT token or null if not found
 */
function getToken() {
    return localStorage.getItem('access_token');
}

/**
 * Set the JWT token
 * @param {string} token - JWT token to store
 */
function setToken(token) {
    localStorage.setItem('access_token', token);
}

/**
 * Remove the JWT token (logout)
 */
function removeToken() {
    localStorage.removeItem('access_token');
}

/**
 * Check if user is authenticated
 * @returns {boolean} true if token exists
 */
function isAuthenticated() {
    return !!getToken();
}

/**
 * Make an authenticated API request
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
async function authenticatedFetch(url, options = {}) {
    const token = getToken();
    
    if (!token) {
        throw new Error('No authentication token found');
    }
    
    // Add authorization header
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    return fetch(url, {
        ...options,
        headers
    });
}

/**
 * Handle API errors and redirect to login if unauthorized
 * @param {Response} response - Fetch response
 * @returns {Promise<any>} Parsed JSON response
 */
async function handleApiResponse(response) {
    if (response.status === 401) {
        // Unauthorized - remove token and redirect to login
        removeToken();
        window.location.href = '/frontend/login.html';
        throw new Error('Unauthorized');
    }
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || 'API request failed');
    }
    
    return data;
}

/**
 * Logout user and redirect to login page
 */
function logout() {
    removeToken();
    window.location.href = '/frontend/login.html';
}
