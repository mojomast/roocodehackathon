"use client";
// frontend/src/app/dashboard/page.tsx
import React, { useState, useEffect } from 'react';
import ErrorBoundary from '../../components/ErrorBoundary';
import ProfileCard from '../../components/ProfileCard';
import Leaderboard from '../../components/Leaderboard';
import { apiClient, APIError } from '../../utils/apiClient';
import GlowingCard from '../../components/GlowingCard';
import { Tabs, TabList, Tab, TabPanels, TabPanel } from '../../components/Tabs';

// Placeholder for a generic LoadingSpinner component
const LoadingSpinner: React.FC = () => (
  <div className="flex justify-center items-center py-4" aria-live="polite" aria-label="Loading content">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
  </div>
);

// Placeholder for a generic ErrorMessage component
const ErrorMessage: React.FC<{ message: string }> = ({ message }) => (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert" aria-live="assertive">
    <strong className="font-bold">Error:</strong>
    <span className="block sm:inline"> {message}</span>
  </div>
);

const DataRow: React.FC<{ label: string; value: React.ReactNode; isLast?: boolean }> = ({ label, value, isLast }) => (
    <div className={`flex justify-between items-center py-3 ${!isLast ? 'border-b border-gray-700' : ''}`}>
        <span className="text-lg text-gray-300">{label}</span>
        <span className="text-lg font-bold text-accent-cyan">{value}</span>
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
  const [screenshots, setScreenshots] = useState<{ url: string; description: string }[]>([]);
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
        setScreenshots((data.screenshots || []).map((url: string) => ({ url, description: 'Screenshot' })));
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
  const points = 0;
  const level = 0;
  const badges: { name: string; icon: string }[] = [];

  return (
    <main className="min-h-screen p-8" role="main">
      <header className="mb-8">
        <h1 className="text-3xl font-bold font-heading text-primary-red">Hack the Planet!</h1>
      </header>

      <section className="mb-8">
       <ProfileCard />
      </section>

     <section className="mb-8">
       <Leaderboard />
     </section>

      <Tabs>
        <TabList>
          <Tab index={0}>Points</Tab>
          <Tab index={1}>Level</Tab>
          <Tab index={2}>Badges</Tab>
          <Tab index={3}>Summary</Tab>
          <Tab index={4}>Recent Screenshots</Tab>
        </TabList>
        <TabPanels>
          <TabPanel index={0}>
            <GlowingCard title="Points">
              <DataRow label="Points" value={points.toLocaleString()} isLast={true} />
            </GlowingCard>
          </TabPanel>
          <TabPanel index={1}>
            <GlowingCard title="Level">
              <DataRow label="Level" value={level} isLast={true} />
            </GlowingCard>
          </TabPanel>
          <TabPanel index={2}>
            <GlowingCard title="Badges">
              <DataRow label="Badges" value={badges.length > 0 ? (
                <div className="flex flex-wrap gap-2 mt-2">
                  {badges.map((badge, index) => (
                    <span key={index} className="bg-accent-purple text-white text-sm font-medium px-2.5 py-0.5 rounded-full flex items-center">
                      {badge.icon} <span className="ml-1">{badge.name}</span>
                    </span>
                  ))}
                </div>
              ) : "None yet!"} isLast={true} />
            </GlowingCard>
          </TabPanel>
          <TabPanel index={3}>
            <GlowingCard title="Summary">
              {loading && <LoadingSpinner />}
              {error && <ErrorMessage message={error} />}
              {!loading && !error && (
                <>
                  <DataRow label="Connected Repositories" value={totalRepos} />
                  <DataRow label="Completed Jobs" value={completedJobs} isLast={true} />
                </>
              )}
            </GlowingCard>
          </TabPanel>
          <TabPanel index={4}>
            <GlowingCard title="Recent Screenshots">
              {loadingScreenshots && <LoadingSpinner />}
              {errorScreenshots && <ErrorMessage message={`Failed to load screenshots: ${errorScreenshots}`} />}
              {!loadingScreenshots && !errorScreenshots && screenshots.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {screenshots.map((screenshot, index) => (
                    <figure key={index} className="bg-gray-900 p-4 rounded-lg">
                      <img src={screenshot.url} alt={screenshot.description} className="w-full h-auto rounded" />
                      <figcaption className="text-sm text-gray-400 mt-2">{screenshot.description}</figcaption>
                    </figure>
                  ))}
                </div>
              )}
              {!loadingScreenshots && !errorScreenshots && screenshots.length === 0 && (
                <p className="text-gray-400">No recent screenshots to display.</p>
              )}
            </GlowingCard>
          </TabPanel>
        </TabPanels>
      </Tabs>
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