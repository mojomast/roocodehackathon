// frontend/src/mocks/handlers.js
import { http, HttpResponse } from 'msw';

export const handlers = [
  // Mock dashboard stats API
  http.get('/api/dashboard/stats', () => {
    return HttpResponse.json({
      totalRepos: 5,
      activeJobs: 12,
      totalPoints: 1250,
      userLevel: 5,
    });
  }),

  // Mock screenshots API
  http.get('/api/screenshots', () => {
    return HttpResponse.json({
      screenshots: [
        'https://placehold.co/600x400',
        'https://placehold.co/600x400',
      ],
    });
  }),

  // Mock gamification API
  http.get('/api/gamification/stats', () => {
    return HttpResponse.json({
      points: 1250,
      level: 5,
      badges: ['First Commit', 'Bug Squasher'],
    });
  }),

  // Mock user profile API
  http.get('/api/user/profile', () => {
    return HttpResponse.json({
      name: 'Test User',
      email: 'test@example.com',
      avatarUrl: 'https://example.com/avatar.png',
    });
  }),

  // Mock auth API for login
  http.get('/api/auth/github', ({ request }) => {
    const url = new URL(request.url);
    const redirect = url.searchParams.get('redirect');
    if (redirect) {
      return new HttpResponse(null, {
        status: 302,
        headers: {
          Location: `/login?redirect=${redirect}`,
        },
      });
    }
    return new HttpResponse(null, {
      status: 302,
      headers: {
        Location: '/login',
      },
    });
  }),

  // Mock API failure scenarios
  http.get('/api/dashboard/stats/fail', () => {
    return new HttpResponse(null, {
      status: 500,
      statusText: 'Internal server error',
    });
  }),

  http.get('/api/screenshots/fail', () => {
    return new HttpResponse(null, {
      status: 500,
      statusText: 'Failed to load screenshots',
    });
  }),
  http.post('/api/repos/connect', () => {
    return HttpResponse.json({ success: true });
  }),
  http.get('/api/repos', () => {
    return HttpResponse.json([]);
  }),
  http.post('/api/docs/run', () => {
    return HttpResponse.json({ success: true });
  }),
  http.get('/api/jobs', () => {
    return HttpResponse.json([]);
  }),
  http.get('http://localhost:8000/api/repos', () => {
    return HttpResponse.json([]);
  }),
  http.post('http://localhost:8000/api/repos/connect', () => {
    return HttpResponse.json({ success: true });
  }),
  http.post('http://localhost:8000/api/docs/run', () => {
    return HttpResponse.json({ success: true });
  }),
  http.get('http://localhost:8000/api/jobs', () => {
    return HttpResponse.json([]);
  }),
  http.get('http://localhost:8000/api/jobs/status/:jobId', () => {
    return HttpResponse.json({
      job_id: 456,
      status: 'completed',
      created_at: '2025-08-29T00:00:00Z',
      updated_at: '2025-08-29T01:00:00Z'
    });
  }),
  http.get('http://localhost:8000/api/dashboard/stats', () => {
    return HttpResponse.json({
      totalRepos: 5,
      activeJobs: 12,
      totalPoints: 1250,
      userLevel: 5,
    });
  }),

  http.get('http://localhost:8000/api/screenshots', () => {
    return HttpResponse.json({
      screenshots: [
        'https://placehold.co/600x400',
        'https://placehold.co/600x400',
      ],
    });
  }),
];