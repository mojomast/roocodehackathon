import { render, waitFor } from '@testing-library/react';
import DashboardPage from './dashboard/page';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';

describe('Performance Tests', () => {
  describe('Load Time Performance', () => {
    test('Dashboard page renders within performance budget', async () => {
      const startTime = performance.now();
      render(<DashboardPage />);
      await waitFor(() => {
        expect(performance.now() - startTime).toBeLessThan(200); // 200ms budget
      });
    });

    test('Concurrent API requests are handled efficiently', async () => {
      const promises = [];
      for (let i = 0; i < 10; i++) {
        promises.push(fetch('/api/dashboard/stats'));
      }
      const startTime = performance.now();
      await Promise.all(promises);
      const loadTime = performance.now() - startTime;
      expect(loadTime).toBeLessThan(500); // 500ms for 10 concurrent requests
    });
  });

  describe('Memory Usage Tests', () => {
    test('Dashboard component memory footprint stays within limits', () => {
      const initialMemory = process.memoryUsage().heapUsed;
      const components = [];
      // Create multiple instances
      for (let i = 0; i < 100; i++) {
        components.push(render(<DashboardPage />));
      }
      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = finalMemory - initialMemory;
      // Expect less than 50MB additional memory
      expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);
      // Cleanup
      components.forEach(component => {
        component.unmount();
      });
    });
  });

  describe('Response Time Tests', () => {
    test('API response time meets performance targets', async () => {
      server.use(
        http.get('/api/dashboard/stats', () => {
          return HttpResponse.json(
            { totalRepos: 5, completedJobs: 12 },
            { delay: 150 }
          );
        })
      );

      const startTime = performance.now();
      await fetch('/api/dashboard/stats');
      const responseTime = performance.now() - startTime;
      expect(responseTime).toBeLessThan(200); // 200ms budget
    });
  });
});