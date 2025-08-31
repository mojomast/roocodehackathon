"use client";
// frontend/src/app/jobs/page.tsx
import React, { useState, useEffect, useRef } from 'react';
import { apiClient, Job, APIError } from '../../utils/apiClient';

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

const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string } | null>(null);
  const [actionLoading, setActionLoading] = useState<{ [key: string]: boolean }>({});

  // Debouncing for polling API calls to prevent excessive requests
  const lastPolledRef = useRef(new Map<number, number>());
  const DEBOUNCE_MS = 1000; // 1 second debounce per job

  // Use ref to ensure only one polling interval is active at a time, preventing memory leaks from multiple intervals
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Job management handler functions
  const handleKillJob = async (jobId: number) => {
    const actionKey = `kill_${jobId}`;
    if (actionLoading[actionKey]) return;

    setActionLoading(prev => ({ ...prev, [actionKey]: true }));
    try {
      await apiClient.killJob(jobId);
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.job_id === jobId ? { ...job, status: 'canceled', updated_at: new Date().toISOString() } : job
        )
      );
    } catch (err) {
      setError({ message: `Failed to kill job ${jobId}` });
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  const handlePauseJob = async (jobId: number) => {
    const actionKey = `pause_${jobId}`;
    if (actionLoading[actionKey]) return;

    setActionLoading(prev => ({ ...prev, [actionKey]: true }));
    try {
      await apiClient.pauseJob(jobId);
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.job_id === jobId ? { ...job, status: 'paused', updated_at: new Date().toISOString() } : job
        )
      );
    } catch (err) {
      setError({ message: `Failed to pause job ${jobId}` });
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  const handleKillAllJobs = async () => {
    const actionKey = 'kill_all';
    if (actionLoading[actionKey]) return;

    setActionLoading(prev => ({ ...prev, [actionKey]: true }));
    try {
      const result = await apiClient.killAllJobs();
      setJobs(prevJobs =>
        prevJobs.map(job =>
          ['pending', 'running', 'paused'].includes(job.status) ? { ...job, status: 'canceled', updated_at: new Date().toISOString() } : job
        )
      );
      alert(result.message);
    } catch (err) {
      setError({ message: 'Failed to kill all jobs' });
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  const handlePauseAllJobs = async () => {
    const actionKey = 'pause_all';
    if (actionLoading[actionKey]) return;

    setActionLoading(prev => ({ ...prev, [actionKey]: true }));
    try {
      const result = await apiClient.pauseAllJobs();
      setJobs(prevJobs =>
        prevJobs.map(job =>
          ['pending', 'running'].includes(job.status) ? { ...job, status: 'paused', updated_at: new Date().toISOString() } : job
        )
      );
      alert(result.message);
    } catch (err) {
      setError({ message: 'Failed to pause all jobs' });
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getJobs();
      setJobs(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError({ message: `Failed to fetch jobs: ${err.message}` });
      } else {
        setError({ message: (err as Error).message });
      }
    } finally {
      setLoading(false);
    }
  };

  const pollJobStatus = async (jobId: number) => {
    // Implement debouncing to prevent excessive API calls for the same job
    const now = Date.now();
    const lastPolled = lastPolledRef.current.get(jobId);
    if (lastPolled !== undefined && now - lastPolled < DEBOUNCE_MS) {
      return; // Skip if recently polled
    }
    lastPolledRef.current.set(jobId, now);

    try {
      const data = await apiClient.getJobStatus(jobId);
      setJobs((prevJobs) =>
        prevJobs.map((job) => (job.job_id === jobId ? { ...job, status: data.status, updated_at: data.updated_at } : job))
      );
    } catch (err) {
      if (err instanceof APIError) {
        console.error(`Failed to fetch status for job ${jobId}: ${err.message}`);
      } else {
        console.error(`Error polling job ${jobId} status:`, err);
      }
    }
  };

  // Fetch jobs on component mount and set up polling only when jobs are available
  useEffect(() => {
    fetchJobs();
  }, []);

  // Separate polling useEffect to manage interval lifecycle and prevent multiple intervals
  useEffect(() => {
    if (jobs.length > 0) {
      // Start polling if not already active
      if (!intervalRef.current) {
        intervalRef.current = setInterval(() => {
          // Poll only jobs that are not completed or failed to minimize unnecessary API calls
          jobs.forEach((job) => {
            if (job.status !== 'completed' && job.status !== 'failed') {
              pollJobStatus(job.job_id);
            }
          });
        }, 5000); // Poll every 5 seconds
      }
    } else {
      // Clear polling if no jobs
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    // Cleanup function to clear interval on unmount or jobs change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [jobs]); // Depend on jobs to start/stop polling based on availability

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'in_progress': return 'text-blue-600';
      case 'pending': return 'text-yellow-600';
      case 'canceled': return 'text-red-500';
      case 'paused': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">View your Documentation Jobs</h1>

      {/* Bulk Action Buttons */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="flex gap-4">
          <button
            onClick={handleKillAllJobs}
            disabled={actionLoading['kill_all']}
            className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {actionLoading['kill_all'] && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
            Kill All Jobs
          </button>
          <button
            onClick={handlePauseAllJobs}
            disabled={actionLoading['pause_all']}
            className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {actionLoading['pause_all'] && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
            Pause All Jobs
          </button>
        </div>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md">
        {loading && <LoadingSpinner />}
        {error && <ErrorMessage message={error.message} />}
        {!loading && !error && (
          jobs.length === 0 ? (
            <p className="text-gray-600">No documentation jobs found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Job ID
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Repository ID
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created At
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Updated
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {jobs.map((job) => (
                    <tr key={job.job_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {job.job_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {job.repo_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`font-semibold ${getStatusColor(job.status)}`}>
                          {job.status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(job.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(job.updated_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          {(job.status === 'pending' || job.status === 'running' || job.status === 'paused') && (
                            <>
                              <button
                                onClick={() => handleKillJob(job.job_id)}
                                disabled={actionLoading[`kill_${job.job_id}`]}
                                className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                              >
                                {actionLoading[`kill_${job.job_id}`] && <div className="animate-spin rounded-full h-3 w-3 border-b border-white"></div>}
                                Kill
                              </button>
                              {job.status !== 'paused' && (
                                <button
                                  onClick={() => handlePauseJob(job.job_id)}
                                  disabled={actionLoading[`pause_${job.job_id}`]}
                                  className="px-3 py-1 bg-orange-500 text-white text-xs rounded hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                                >
                                  {actionLoading[`pause_${job.job_id}`] && <div className="animate-spin rounded-full h-3 w-3 border-b border-white"></div>}
                                  Pause
                                </button>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default JobsPage;