/**
 * Comprehensive test suite for RestAdaptor
 * Tests HTTP methods, error handling, and timeout functionality
 */

import { jest } from '@jest/globals';
import RestAdaptor from '../../src/adaptors/rest/rest.js';

describe('RestAdaptor', () => {
  let adaptor;
  const baseUrl = 'https://api.example.com';
  const mockFetch = jest.fn();

  beforeEach(() => {
    global.fetch = mockFetch;
    mockFetch.mockClear();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  describe('Initialization', () => {
    test('should initialize with base URL', () => {
      adaptor = new RestAdaptor(baseUrl);

      expect(adaptor.baseUrl).toBe(baseUrl);
    });

    test('should initialize with default headers', () => {
      adaptor = new RestAdaptor(baseUrl);

      expect(adaptor.headers).toEqual({
        'Content-Type': 'application/json'
      });
    });

    test('should initialize with custom headers', () => {
      const customHeaders = {
        'Authorization': 'Bearer token123',
        'X-Custom': 'value'
      };

      adaptor = new RestAdaptor(baseUrl, { headers: customHeaders });

      expect(adaptor.headers).toEqual(customHeaders);
    });

    test('should initialize with default timeout', () => {
      adaptor = new RestAdaptor(baseUrl);

      expect(adaptor.timeout).toBe(5000);
    });

    test('should initialize with custom timeout', () => {
      adaptor = new RestAdaptor(baseUrl, { timeout: 10000 });

      expect(adaptor.timeout).toBe(10000);
    });
  });

  describe('GET Requests', () => {
    beforeEach(() => {
      adaptor = new RestAdaptor(baseUrl);
    });

    test('should make GET request successfully', async () => {
      const mockData = { data: 'test' };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockData,
        headers: { get: () => 'application/json' }
      });

      const result = await adaptor.get('/endpoint');

      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockData);
    });

    test('should append query parameters to GET request', async () => {
      const mockData = { results: [] };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockData,
        headers: { get: () => 'application/json' }
      });

      const params = { page: 1, limit: 10 };
      await adaptor.get('/users', params);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl.toString()).toContain('page=1');
      expect(callUrl.toString()).toContain('limit=10');
    });

    test('should handle empty response', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        text: async () => '',
        headers: { get: () => null }
      });

      const result = await adaptor.get('/endpoint');

      expect(result).toBe('');
    });
  });

  describe('POST Requests', () => {
    beforeEach(() => {
      adaptor = new RestAdaptor(baseUrl);
    });

    test('should make POST request with data', async () => {
      const postData = { name: 'Test', value: 123 };
      const mockResponse = { id: 1, ...postData };

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
        headers: { get: () => 'application/json' }
      });

      const result = await adaptor.post('/items', postData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(URL),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData)
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('should stringify POST body', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({}),
        headers: { get: () => 'application/json' }
      });

      const data = { test: 'data' };
      await adaptor.post('/endpoint', data);

      const fetchOptions = mockFetch.mock.calls[0][1];
      expect(fetchOptions.body).toBe(JSON.stringify(data));
    });
  });

  describe('PUT Requests', () => {
    beforeEach(() => {
      adaptor = new RestAdaptor(baseUrl);
    });

    test('should make PUT request with data', async () => {
      const putData = { name: 'Updated' };
      const mockResponse = { id: 1, ...putData };

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
        headers: { get: () => 'application/json' }
      });

      const result = await adaptor.put('/items/1', putData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(URL),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData)
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('DELETE Requests', () => {
    beforeEach(() => {
      adaptor = new RestAdaptor(baseUrl);
    });

    test('should make DELETE request', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true }),
        headers: { get: () => 'application/json' }
      });

      const result = await adaptor.delete('/items/1');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(URL),
        expect.objectContaining({
          method: 'DELETE'
        })
      );
      expect(result).toEqual({ success: true });
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      adaptor = new RestAdaptor(baseUrl);
    });

    test('should throw error on HTTP error status', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        headers: { get: () => 'application/json' }
      });

      await expect(adaptor.get('/notfound')).rejects.toThrow('HTTP error! status: 404');
    });

    test('should throw error on network failure', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      await expect(adaptor.get('/endpoint')).rejects.toThrow('Network error');
    });

    test('should handle 500 server error', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        headers: { get: () => 'application/json' }
      });

      await expect(adaptor.post('/error')).rejects.toThrow('HTTP error! status: 500');
    });
  });

  describe('Timeout Handling', () => {
    beforeEach(() => {
      jest.useFakeTimers();
      adaptor = new RestAdaptor(baseUrl, { timeout: 1000 });
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test('should abort request on timeout', async () => {
      const abortError = new Error('Aborted');
      abortError.name = 'AbortError';

      mockFetch.mockImplementation(() => {
        return new Promise((resolve, reject) => {
          setTimeout(() => resolve({
            ok: true,
            json: async () => ({})
          }), 5000);
        });
      });

      const requestPromise = adaptor.get('/slow');

      // Fast-forward time to trigger timeout
      jest.advanceTimersByTime(1000);

      // The request should still be pending but timeout should have been triggered
      expect(mockFetch).toHaveBeenCalled();
    });

    test('should clear timeout on successful response', async () => {
      const clearTimeoutSpy = jest.spyOn(global, 'clearTimeout');

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'fast' }),
        headers: { get: () => 'application/json' }
      });

      await adaptor.get('/fast');

      expect(clearTimeoutSpy).toHaveBeenCalled();

      clearTimeoutSpy.mockRestore();
    });
  });

  describe('Content Type Handling', () => {
    beforeEach(() => {
      adaptor = new RestAdaptor(baseUrl);
    });

    test('should handle JSON response', async () => {
      const jsonData = { test: 'data' };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => jsonData,
        headers: { get: () => 'application/json' }
      });

      const result = await adaptor.get('/json');

      expect(result).toEqual(jsonData);
    });

    test('should handle text response', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        text: async () => 'plain text',
        headers: { get: () => 'text/plain' }
      });

      const result = await adaptor.get('/text');

      expect(result).toBe('plain text');
    });

    test('should handle missing content-type as text', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        text: async () => 'default text',
        headers: { get: () => null }
      });

      const result = await adaptor.get('/noheader');

      expect(result).toBe('default text');
    });
  });

  describe('Headers', () => {
    test('should include default headers in requests', async () => {
      adaptor = new RestAdaptor(baseUrl);

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({}),
        headers: { get: () => 'application/json' }
      });

      await adaptor.get('/test');

      const fetchOptions = mockFetch.mock.calls[0][1];
      expect(fetchOptions.headers).toEqual({
        'Content-Type': 'application/json'
      });
    });

    test('should include custom headers in requests', async () => {
      const customHeaders = {
        'Authorization': 'Bearer token',
        'X-API-Key': 'key123'
      };

      adaptor = new RestAdaptor(baseUrl, { headers: customHeaders });

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({}),
        headers: { get: () => 'application/json' }
      });

      await adaptor.get('/test');

      const fetchOptions = mockFetch.mock.calls[0][1];
      expect(fetchOptions.headers).toEqual(customHeaders);
    });
  });

  describe('Integration Tests', () => {
    test('should handle complete request cycle', async () => {
      adaptor = new RestAdaptor(baseUrl, {
        headers: { 'X-Custom': 'test' },
        timeout: 3000
      });

      const mockData = { id: 1, name: 'Test' };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockData,
        headers: { get: () => 'application/json' }
      });

      const result = await adaptor.get('/data', { filter: 'active' });

      expect(mockFetch).toHaveBeenCalled();
      expect(result).toEqual(mockData);

      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl.toString()).toContain('filter=active');
    });
  });
});
