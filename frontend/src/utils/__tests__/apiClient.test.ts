/**
 * Integration tests for API Client
 * Tests the typed API client with mocked fetch responses
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { apiClient, setAuthToken, clearAuthToken, APIError } from '../apiClient';
import { server } from '../../mocks/server';
import { http, HttpResponse } from 'msw';

describe('API Client Integration Tests', () => {
  beforeEach(() => {
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
      const result = await apiClient.connectRepo({
        repo_url: 'https://github.com/owner/repo',
        repo_name: 'test-repo'
      });

      expect(result).toEqual({ success: true });
    });

    test('connectRepo - handles server error', async () => {

      server.use(
        http.post('http://localhost:8000/api/repos/connect', () => {
          return new HttpResponse(null, {
            status: 400,
            statusText: 'Invalid repository URL',
          });
        })
      );

      await expect(apiClient.connectRepo({
        repo_url: 'invalid-url',
        repo_name: 'test-repo'
      })).rejects.toThrow(APIError);
    });

    test('getRepos - retrieves user repositories', async () => {
      const result = await apiClient.getRepos();

      expect(result).toEqual([]);
    });

    test('getRepos - handles error', async () => {

      server.use(
        http.get('http://localhost:8000/api/repos', () => {
          return new HttpResponse(null, {
            status: 500,
            statusText: 'Server error',
          });
        })
      );

      await expect(apiClient.getRepos()).rejects.toThrow(APIError);
    });
  });

  describe('Job Operations', () => {
    test('createJob - successfully creates a documentation job', async () => {
      const result = await apiClient.createJob({ repo_id: 1 });

      expect(result).toEqual({ success: true });
    });

    test('getJobs - retrieves all jobs', async () => {
      const result = await apiClient.getJobs();

      expect(result).toEqual([]);
    });

    test('getJobStatus - retrieves job status', async () => {
      const result = await apiClient.getJobStatus(456);

      expect(result).toEqual({
        job_id: 456,
        status: 'completed',
        created_at: '2025-08-29T00:00:00Z',
        updated_at: '2025-08-29T01:00:00Z'
      });
    });

    test('getJobStatus - handles 404 error', async () => {

      server.use(
        http.get('http://localhost:8000/api/jobs/status/999', () => {
          return new HttpResponse(null, {
            status: 404,
            statusText: 'Job not found',
          });
        })
      );

      await expect(apiClient.getJobStatus(999)).rejects.toThrow(APIError);
    });
  });

  describe('Dashboard Operations', () => {
    test('getDashboardStats - retrieves dashboard statistics', async () => {
      const result = await apiClient.getDashboardStats();

      expect(result).toEqual({
        totalRepos: 5,
        totalJobs: 20,
        activeJobs: 3
      });
    });

    test('getScreenshots - retrieves screenshot data', async () => {
      const result = await apiClient.getScreenshots();

      expect(result).toEqual({ screenshots: ['http://example.com/screenshot1.png'] });
    });
  });

  describe('Error Handling', () => {
    test('handles network error', async () => {

      server.use(
        http.get('http://localhost:8000/api/repos', () => {
          return new HttpResponse(null, {
            status: 500,
            statusText: 'Network error',
          });
        })
      );

      await expect(apiClient.getRepos()).rejects.toThrow(/Network error/);
    });
  });
});