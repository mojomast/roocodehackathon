// frontend/src/app/dashboard/page.tsx
import React, { useState, useEffect } from 'react';
import ErrorBoundary from '../../components/ErrorBoundary';
import { apiClient, APIError } from '../../utils/apiClient';

// Placeholder for a generic LoadingSpinner component
const LoadingSpinner: React.FC = () => (
  <div className="flex justify-center items-center py-4">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
  </div>
);

// Placeholder for a generic ErrorMessage component
const ErrorMessage: React.FC<{ message: string }> = ({ message }) => (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
    <strong className="font-bold">Error:</strong>
    <span className="block sm:inline"> {message}</span>
  </div>
);

/**
 * Renders the main Dashboard page.
 * Includes placeholder content for welcome message and gamification elements.
 */
const DashboardPageContent: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalRepos, setTotalRepos] = useState<number | null>(null);
  const [completedJobs, setCompletedJobs] = useState<number | null>(null);

  // FE-004: Screenshots component state and loading
  const [screenshots, setScreenshots] = useState<any[]>([]);
  const [loadingScreenshots, setLoadingScreenshots] = useState(true);
  const [errorScreenshots, setErrorScreenshots] = useState<string | null>(null);

  // Fetch dashboard stats
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getDashboardStats();
        setTotalRepos(data.totalRepos);
        setCompletedJobs(data.activeJobs); // Note: adjusted to match interface
      } catch (err) {
        if (err instanceof APIError) {
          setError(`Failed to fetch dashboard stats: ${err.message}`);
        } else {
          setError((err as Error).message);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Fetch screenshots data for the component
  useEffect(() => {
    const fetchScreenshotsData = async () => {
      try {
        setLoadingScreenshots(true);
        setErrorScreenshots(null);
        const data = await apiClient.getScreenshots();
        setScreenshots(data.screenshots || []);
      } catch (err) {
        if (err instanceof APIError) {
          setErrorScreenshots(`Failed to fetch screenshots: ${err.message}`);
        } else {
          setErrorScreenshots((err as Error).message);
        }
      } finally {
        setLoadingScreenshots(false);
      }
    };

    fetchScreenshotsData();
  }, []);

  // Hardcoded gamification values
  const points = 1250;
  const level = 5;
  const badges = [
    { name: 'First Commit', icon: '🌟' },
    { name: 'Bug Hunter', icon: '🐞' },
    { name: 'Code Master', icon: '🏆' },
  ];

  return (
    <main className="min-h-screen bg-gray-100 p-8" role="main">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Welcome to the Dashboard!</h1>
      </header>

      {/* Gamification Elements */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Points</h2>
          <p className="text-2xl text-blue-600">{points.toLocaleString()}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Level</h2>
          <p className="text-2xl text-green-600">{level}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Badges</h2>
          <div className="flex flex-wrap gap-2 mt-2">
            {badges.map((badge, index) => (
              <span key={index} className="bg-purple-100 text-purple-800 text-sm font-medium px-2.5 py-0.5 rounded-full flex items-center">
                {badge.icon} <span className="ml-1">{badge.name}</span>
              </span>
            ))}
            {badges.length === 0 && <p className="text-gray-500 text-lg">None yet!</p>}
          </div>
        </div>
      </div>

      {/* Summary Data */}
      <div className="bg-white p-8 rounded-lg shadow-md mb-8">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Summary</h2>
        {loading && <LoadingSpinner />}
        {error && <ErrorMessage message={error} />}
        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-gray-600">Connected Repositories</h3>
              <p className="text-3xl font-bold text-blue-700">{totalRepos}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-gray-600">Completed Jobs</h3>
              <p className="text-3xl font-bold text-green-700">{completedJobs}</p>
            </div>
          </div>
        )}
      </div>

      {/* FE-004: Screenshots component with loading states and error handling */}
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Recent Screenshots</h2>
        {loadingScreenshots && <LoadingSpinner />}
        {errorScreenshots && <ErrorMessage message={`Failed to load screenshots: ${errorScreenshots}`} />}
        {!loadingScreenshots && !errorScreenshots && screenshots.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {screenshots.map((screenshot, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg">
                <img src={screenshot.url} alt={screenshot.description} className="w-full h-auto" />
                <p className="text-sm text-gray-600 mt-2">{screenshot.description}</p>
              </div>
            ))}
          </div>
        )}
        {!loadingScreenshots && !errorScreenshots && screenshots.length === 0 && (
          <p className="text-gray-600">No recent screenshots to display.</p>
        )}
      </div>
    </main>
  );
};

// FE-004: Wrap DashboardPage with ErrorBoundary for comprehensive component error handling
const DashboardPage: React.FC = () => {
  return (
    <ErrorBoundary>
      <DashboardPageContent />
    </ErrorBoundary>
  );
};

export default DashboardPage;