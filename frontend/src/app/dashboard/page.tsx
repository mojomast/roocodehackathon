// frontend/src/app/dashboard/page.tsx
import React, { useState, useEffect } from 'react';

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
const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalRepos, setTotalRepos] = useState<number | null>(null);
  const [completedJobs, setCompletedJobs] = useState<number | null>(null);

  // Simulate data fetching
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Simulate successful data
        setTotalRepos(12);
        setCompletedJobs(78);

        // Simulate an error for testing:
        // throw new Error("Failed to fetch dashboard data.");

      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
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
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Welcome to the Dashboard!</h1>

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

      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Your Activity</h2>
        <p className="text-gray-600">No recent activity to display.</p>
      </div>
    </div>
  );
};

export default DashboardPage;