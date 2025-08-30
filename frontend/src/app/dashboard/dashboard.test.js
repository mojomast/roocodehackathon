import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { server } from '../../mocks/server';
import { rest } from 'msw';
import DashboardPage from './page';

describe('DashboardPage', () => {
  it('renders a heading', () => {
    render(<DashboardPage />);
    const heading = screen.getByRole('heading', { name: /Welcome to the Dashboard!/i });
    expect(heading).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    render(<DashboardPage />);

    // Check for loading spinner (animate-spin class)
    const loadingElements = screen.getAllByText(/Loading/i);
    expect(loadingElements.length).toBeGreaterThan(0);
  });

  it('fetches and displays dashboard stats with correct data', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
    });

    // Verify specific stats are displayed correctly
    expect(screen.getByText('Connected Repositories')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Completed Jobs')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('handles API error for dashboard stats', async () => {
    // Mock API failure
    server.use(
      rest.get('/api/dashboard/stats', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Internal server error' }));
      })
    );

    render(<DashboardPage />);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText(/HTTP error! status: 500/i)).toBeInTheDocument();
    });

    // Ensure stats are not shown when there's an error
    expect(screen.queryByText('Connected Repositories')).not.toBeInTheDocument();
  });

  it('displays screenshots with correct alt text and sources', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Recent Screenshots')).toBeInTheDocument();
    });

    // Verify screenshot content and attributes
    expect(screen.getByText('Homepage')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();

    const images = screen.getAllByRole('img');
    expect(images).toHaveLength(2);
    expect(images[0]).toHaveAttribute('src', 'https://example.com/screenshot1.png');
    expect(images[0]).toHaveAttribute('alt', 'Homepage screenshot');
    expect(images[1]).toHaveAttribute('src', 'https://example.com/screenshot2.png');
    expect(images[1]).toHaveAttribute('alt', 'Dashboard screenshot');
  });

  it('handles screenshots API error', async () => {
    // Mock screenshots API failure
    server.use(
      rest.get('/api/screenshots', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Failed to load screenshots' }));
      })
    );

    render(<DashboardPage />);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to load screenshots: HTTP error! status: 500/i)).toBeInTheDocument();
    });
  });

  it('shows no screenshots message when empty', async () => {
    // Mock empty screenshots response
    server.use(
      rest.get('/api/screenshots', (req, res, ctx) => {
        return res(ctx.json({ screenshots: [] }));
      })
    );

    render(<DashboardPage />);

    // Wait for "no screenshots" message
    await waitFor(() => {
      expect(screen.getByText('No recent screenshots to display.')).toBeInTheDocument();
    });
  });

  it('displays gamification elements with correct data', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
    });

    // Verify gamification data is displayed correctly
    expect(screen.getByText('Points')).toBeInTheDocument();
    expect(screen.getByText('1,250')).toBeInTheDocument();
    expect(screen.getByText('Level')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Badges')).toBeInTheDocument();
    expect(screen.getByText('First Commit')).toBeInTheDocument();
    expect(screen.getByText('Bug Squasher')).toBeInTheDocument();
  });
});