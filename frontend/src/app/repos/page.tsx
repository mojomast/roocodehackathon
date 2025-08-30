"use client";
// frontend/src/app/repos/page.tsx
import React, { useState, useEffect } from 'react';
import { apiClient, Repo, APIError } from '../../utils/apiClient';

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
 * Renders the Repositories page.
 * This page is for connecting and managing GitHub repositories.
 */
const ReposPage: React.FC = () => {
  const [repoName, setRepoName] = useState<string>('');
  const [repoUrl, setRepoUrl] = useState<string>('');
  const [connectMessage, setConnectMessage] = useState<string>('');
  const [fetchMessage, setFetchMessage] = useState<string>('');
  const [repos, setRepos] = useState<Repo[]>([]);
  const [loadingRepos, setLoadingRepos] = useState<boolean>(true);
  const [connectingRepo, setConnectingRepo] = useState<boolean>(false);
  const [runningAnalysis, setRunningAnalysis] = useState<number | null>(null); // Stores repoId being analyzed

  const fetchRepos = async () => {
    setLoadingRepos(true);
    setFetchMessage('');
    try {
      const data = await apiClient.getRepos();
      setRepos(data);
    } catch (error) {
      if (error instanceof APIError) {
        setFetchMessage(`Failed to fetch repositories: ${error.message}`);
      } else {
        setFetchMessage('Error fetching repositories.');
        console.error('Error fetching repos:', error);
      }
    } finally {
      setLoadingRepos(false);
    }
  };

  useEffect(() => {
    fetchRepos();
  }, []);

  const handleConnectRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    setConnectMessage('');
    setConnectingRepo(true);

    try {
      const data = await apiClient.connectRepo({ repo_name: repoName, repo_url: repoUrl });
      setConnectMessage(data.message || 'Repository connected successfully!');
      setRepoName('');
      setRepoUrl('');
      fetchRepos(); // Refresh the list of repositories
    } catch (error) {
      if (error instanceof APIError) {
        setConnectMessage(`Failed to connect repository: ${error.message}`);
      } else {
        setConnectMessage('Error connecting repository.');
        console.error('Error connecting repo:', error);
      }
    } finally {
      setConnectingRepo(false);
    }
  };

  const handleRunAnalysis = async (repoId: number) => {
    setConnectMessage(''); // Clear previous messages
    setRunningAnalysis(repoId);
    try {
      const data = await apiClient.createJob({ repo_id: repoId });
      setConnectMessage(data.message || 'Analysis triggered successfully!');
    } catch (error) {
      if (error instanceof APIError) {
        setConnectMessage(`Failed to trigger analysis: ${error.message}`);
      } else {
        setConnectMessage(`Error triggering analysis for repo ID ${repoId}.`);
        console.error('Error triggering analysis:', error);
      }
    } finally {
      setRunningAnalysis(null);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-8" role="main">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Connect your GitHub Repositories</h1>
      </header>
      <div className="bg-white p-8 rounded-lg shadow-md mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">Connect New Repository</h2>
        <form onSubmit={handleConnectRepo} className="space-y-4">
          <div>
            <label htmlFor="repoName" className="block text-sm font-medium text-gray-700">
              Repository Name
            </label>
            <input
              type="text"
              id="repoName"
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              value={repoName}
              onChange={(e) => setRepoName(e.target.value)}
              required
              disabled={connectingRepo}
            />
          </div>
          <div>
            <label htmlFor="repoUrl" className="block text-sm font-medium text-gray-700">
              Repository URL
            </label>
            <input
              type="url"
              id="repoUrl"
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              required
              disabled={connectingRepo}
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={connectingRepo}
          >
            {connectingRepo ? 'Connecting...' : 'Connect Repository'}
          </button>
        </form>
        {connectMessage && (
          <p className={`mt-4 text-sm ${connectMessage.includes('successfully') ? 'text-green-600' : 'text-red-600'}`}>
            {connectMessage}
          </p>
        )}
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">Connected Repositories</h2>
        {loadingRepos && <LoadingSpinner />}
        {fetchMessage && <ErrorMessage message={fetchMessage} />}
        {!loadingRepos && !fetchMessage && (
          repos.length === 0 ? (
            <p className="text-gray-600">No repositories connected yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {repos.map((repo) => (
                <div key={repo.id} className="bg-gray-50 p-4 rounded-lg shadow-sm border border-gray-200">
                  <p className="text-lg font-medium text-gray-900 truncate" title={repo.repo_name}>{repo.repo_name}</p>
                  <a
                    href={repo.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline truncate block"
                    title={repo.repo_url}
                  >
                    {repo.repo_url}
                  </a>
                  <button
                    onClick={() => handleRunAnalysis(repo.id)}
                    className="mt-3 w-full px-3 py-1 bg-green-600 text-white font-semibold rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={runningAnalysis === repo.id}
                  >
                    {runningAnalysis === repo.id ? 'Analyzing...' : 'Run Analysis'}
                  </button>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </main>
  );
};

export default ReposPage;