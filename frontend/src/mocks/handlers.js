// frontend/src/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  // Mock dashboard stats API
  rest.get('/api/dashboard/stats', (req, res, ctx) => {
    return res(ctx.json({
      totalRepos: 5,
      completedJobs: 12
    }));
  }),

  // Mock screenshots API
  rest.get('/api/screenshots', (req, res, ctx) => {
    return res(ctx.json({
      screenshots: [
        {
          url: 'https://example.com/screenshot1.png',
          description: 'Homepage'
        },
        {
          url: 'https://example.com/screenshot2.png',
          description: 'Dashboard'
        }
      ]
    }));
  }),

  // Mock auth API for login
  rest.get('/api/auth/github', (req, res, ctx) => {
    const redirect = req.url.searchParams.get('redirect');
    if (redirect) {
      return res(ctx.status(302), ctx.set('Location', `/login?redirect=${redirect}`));
    }
    return res(ctx.status(302), ctx.set('Location', '/login'));
  }),

  // Mock API failure scenarios
  rest.get('/api/dashboard/stats/fail', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ error: 'Internal server error' }));
  }),

  rest.get('/api/screenshots/fail', (req, res, ctx) => {
    return res(ctx.networkError(), ctx.text('Network error'));
  }),
];