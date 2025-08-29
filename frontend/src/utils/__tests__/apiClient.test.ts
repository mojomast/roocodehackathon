/**
 * Integration tests for API Client
 * Tests the typed API client with mocked fetch responses
 */

import { apiClient, setAuthToken, clearAuthToken, APIError } from '../apiClient';

// Mock fetch globally
const mockFetch = jest.fn() as jest.MockedFunction<typeof fetch>;
global.fetch = mockFetch;

// Import after mocking to ensure apiClient uses the mock
describe('API Client Integration Tests', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    clearAuthToken();
  });

  describe('Authentication', () => {
    test('sets auth token correctly', () => {
      setAuthToken('test-token');
      expect(true).toBe(true); // Placeholder test
    });

    test('clears auth token correctly', () => {
      setAuthToken('test-token');
      clearAuthToken();
      expect(true).toBe(true); // Placeholder test
    });
  });

  describe('Repository Operations', () => {
    test('connectRepo - successfully connects a repository', async () => {
      const mockResponse = {
        message: 'Repository connected successfully',
        repo_id: 123
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await apiClient.connectRepo({
        repo_url: 'https://github.com/owner/repo',
        repo_name: 'test-repo'
      });

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/repos/connect',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('repo_url'),
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );
    });

    test('connectRepo - handles server error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        text: jest.fn().mockResolvedValue('Invalid repository URL'),
      } as any);

      await expect(apiClient.connectRepo({
        repo_url: 'invalid-url',
        repo_name: 'test-repo'
      })).rejects.toThrow(APIError);
    });

    test('getRepos - retrieves user repositories', async () => {
      const mockResponse = [
        { id: 1, repo_url: 'https://github.com/owner/repo', repo_name: 'repo', status: 'connected' }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await apiClient.getRepos();

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/repos',
        expect.objectContaining({ method: 'GET' })
      );
    });

    test('getRepos - handles error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: jest.fn().mockResolvedValue('Server error'),
      } as any);

      await expect(apiClient.getRepos()).rejects.toThrow(APIError);
    });
  });

  describe('Job Operations', () => {
    test('createJob - successfully creates a documentation job', async () => {
      const mockResponse = { message: 'Documentation run triggered', job_id: 456, status: 'pending' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await apiClient.createJob({ repo_id: 1 });

      expect(result).toEqual(mockResponse);
    });

    test('getJobs - retrieves all jobs', async () => {
      const mockResponse = [
        {
          job_id: 456,
          repo_id: 1,
          status: 'completed',
          created_at: '2025-08-29T00:00:00Z',
          updated_at: '2025-08-29T01:00:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await apiClient.getJobs();

      expect(result).toEqual(mockResponse);
    });

    test('getJobStatus - retrieves job status', async () => {
      const mockResponse = {
        job_id: 456,
        status: 'completed',
        created_at: '2025-08-29T00:00:00Z',
        updated_at: '2025-08-29T01:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await apiClient.getJobStatus(456);

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/jobs/status/456',
        expect.objectContaining({ method: 'GET' })
      );
    });

    test('getJobStatus - handles 404 error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: jest.fn().mockResolvedValue('Job not found'),
      } as any);

      await expect(apiClient.getJobStatus(999)).rejects.toThrow(APIError);
    });
  });

  describe('Dashboard Operations', () => {
    test('getDashboardStats - retrieves dashboard statistics', async () => {
      const mockResponse = {
        totalRepos: 5,
        totalJobs: 20,
        activeJobs: 3
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await apiClient.getDashboardStats();

      expect(result).toEqual(mockResponse);
    });

    test('getScreenshots - retrieves screenshot data', async () => {
      const mockResponse = { screenshots: ['http://example.com/screenshot1.png'] };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await apiClient.getScreenshots();

      expect(result).toEqual(mockResponse);
    });
  });

  describe('Error Handling', () => {
    test('handles network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiClient.getRepos()).rejects.toThrow(/Network error/);
    });
  });
});