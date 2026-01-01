/**
 * REST Adaptor
 * Handles HTTP REST API communication
 */

class RestAdaptor {
  constructor(baseUrl, options = {}) {
    this.baseUrl = baseUrl;
    this.headers = options.headers || {
      'Content-Type': 'application/json',
    };
    this.timeout = options.timeout || 5000;
  }

  /**
   * Make a GET request
   */
  async get(endpoint, params = {}) {
    const url = new URL(endpoint, this.baseUrl);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    
    return this._fetch(url, { method: 'GET' });
  }

  /**
   * Make a POST request
   */
  async post(endpoint, data) {
    const url = new URL(endpoint, this.baseUrl);
    return this._fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Make a PUT request
   */
  async put(endpoint, data) {
    const url = new URL(endpoint, this.baseUrl);
    return this._fetch(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Make a DELETE request
   */
  async delete(endpoint) {
    const url = new URL(endpoint, this.baseUrl);
    return this._fetch(url, { method: 'DELETE' });
  }

  /**
   * Internal fetch wrapper with timeout and error handling
   */
  async _fetch(url, options) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: this.headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }
}

export default RestAdaptor;
