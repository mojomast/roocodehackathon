/**
 * Typed API Client for FixMyDocs Frontend
 * Handles base URL configuration, authentication, error handling, and SSR compatibility
 */

export class APIError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

// Auth token management
let authToken: string | null = null;

export function setAuthToken(token: string): void {
  authToken = token;
}

export function clearAuthToken(): void {
  authToken = null;
}

// Base URL configuration - server/client aware
const getBaseUrl = (): string => {
  const envUrl = process.env['NEXT_PUBLIC_API_URL'];
  return envUrl || 'http://localhost:8000';
};

// API request function
async function apiRequest(endpoint: string, options: any = {}): Promise<any> {
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}${endpoint}`;

  const headers = new Headers({
    'Content-Type': 'application/json',
  });

  if (authToken) {
    headers.set('X-Auth-Token', authToken);
  }

  if (options.headers) {
    for (const [key, value] of Object.entries(options.headers)) {
      headers.set(key, String(value));
    }
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  if ((options as any).body && typeof (options as any).body === 'object' && !((options as any).body instanceof FormData)) {
    (config as any).body = JSON.stringify((options as any).body);
  }

  try {
    const res = await fetch(url, config);

    if (!res.ok) {
      let errorMessage = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errorData = await res.text();
        errorMessage = errorData || errorMessage;
      } catch {
        // Use default error message
      }
      throw new APIError(errorMessage, res.status);
    }

    return await res.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`, 0);
  }
}

// Type definitions for API requests/responses
export interface RepoConnectRequest {
  repo_url: string;
  repo_name: string;
}

export interface RepoConnectResponse {
  message: string;
  repo_id: number;
}

export interface JobCreateRequest {
  repo_id: number;
}

export interface JobCreateResponse {
  message: string;
  job_id: number;
  status: string;
}

export interface Job {
  job_id: number;
  repo_id: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface JobStatusResponse {
  job_id: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Repo {
  id: number;
  repo_url: string;
  repo_name: string;
  status: string;
}

export interface DashboardStatsResponse {
  // Placeholder - define based on actual API response
  totalRepos: number;
  totalJobs: number;
  activeJobs: number;
}

export interface ScreenshotsResponse {
  // Placeholder - define based on actual API response
  screenshots: string[]; // URLs or base64
}

// API client functions - typed and standardized
export const apiClient = {
  // Repository management
  connectRepo: (data: RepoConnectRequest): Promise<RepoConnectResponse> =>
    apiRequest('/api/repos/connect', { method: 'POST', body: data }),

  getRepos: (): Promise<Repo[]> =>
    apiRequest('/api/repos', { method: 'GET' }),

  // Job management
  createJob: (data: JobCreateRequest): Promise<JobCreateResponse> =>
    apiRequest('/api/docs/run', { method: 'POST', body: data }),

  getJobs: (): Promise<Job[]> =>
    apiRequest('/api/jobs', { method: 'GET' }),

  getJobStatus: (jobId: number): Promise<JobStatusResponse> =>
    apiRequest(`/api/jobs/status/${jobId}`, { method: 'GET' }),

  // Dashboard (placeholder endpoints - to be updated when backend implements)
  getDashboardStats: (): Promise<DashboardStatsResponse> =>
    apiRequest('/api/dashboard/stats', { method: 'GET' }),

  getScreenshots: (): Promise<ScreenshotsResponse> =>
    apiRequest('/api/screenshots', { method: 'GET' }),
};

export default apiClient;