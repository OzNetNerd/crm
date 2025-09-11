/**
 * Essential API Client - Minimal fetch wrapper for HTMX-based application
 * 
 * Provides only basic fetch functionality. Most API operations now handled
 * via HTMX forms and server-side processing.
 */

class CRMApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generic fetch wrapper with basic error handling
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} Response data
     */
    async request(url, options = {}) {
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(`${this.baseUrl}${url}`, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(url, options = {}) {
        return this.request(url, { method: 'GET', ...options });
    }

    /**
     * POST request
     */
    async post(url, data = null, options = {}) {
        return this.request(url, {
            method: 'POST',
            body: data ? JSON.stringify(data) : null,
            ...options
        });
    }
}

// Create global API instance for backwards compatibility
const api = new CRMApiClient();
window.api = api;
window.CRMApiClient = CRMApiClient;