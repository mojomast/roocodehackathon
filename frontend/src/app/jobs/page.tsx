// frontend/src/app/jobs/page.tsx
import React, { useState, useEffect } from 'react';

interface Job {
  job_id: number;
  repo_id: number;
  status: string;
  created_at: string;
  updated_at: string;
}

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
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Simulate fetching data
      const dummyJobs: Job[] = [
        { job_id: 1, repo_id: 101, status: 'completed', created_at: new Date(Date.now() - 86400000 * 2).toISOString(), updated_at: new Date(Date.now() - 86400000 * 2 + 3600000).toISOString() },
        { job_id: 2, repo_id: 102, status: 'in_progress', created_at: new Date(Date.now() - 86400000).toISOString(), updated_at: new Date(Date.now() - 86400000 + 1800000).toISOString() },
        { job_id: 3, repo_id: 101, status: 'failed', created_at: new Date(Date.now() - 86400000 * 0.5).toISOString(), updated_at: new Date(Date.now() - 86400000 * 0.5 + 600000).toISOString() },
        { job_id: 4, repo_id: 103, status: 'pending', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      ];
      setJobs(dummyJobs);

      // Simulate an error for testing:
      // throw new Error("Failed to fetch jobs data.");

      // const response = await fetch('/api/jobs');
      // if (response.ok) {
      //   const data = await response.json();
      //   setJobs(data);
      // } else {
      //   setError('Failed to fetch jobs.');
      // }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const pollJobStatus = async (jobId: number) => {
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));

      // Simulate status update
      const updatedStatus = Math.random() > 0.7 ? 'completed' : 'in_progress'; // Randomly complete some jobs
      setJobs((prevJobs) =>
        prevJobs.map((job) =>
          job.job_id === jobId
            ? { ...job, status: updatedStatus, updated_at: new Date().toISOString() }
            : job
        )
      );

      // const response = await fetch(`/api/jobs/status/${jobId}`);
      // if (response.ok) {
      //   const data = await response.json();
      //   setJobs((prevJobs) =>
      //     prevJobs.map((job) => (job.job_id === jobId ? { ...job, status: data.status, updated_at: data.updated_at } : job))
      //   );
      // } else {
      //   console.error(`Failed to fetch status for job ${jobId}`);
      // }
    } catch (err) {
      console.error(`Error polling job ${jobId} status:`, err);
    }
  };

  useEffect(() => {
    fetchJobs();

    const interval = setInterval(() => {
      jobs.forEach((job) => {
        if (job.status !== 'completed' && job.status !== 'failed') {
          pollJobStatus(job.job_id);
        }
      });
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [jobs]); // Re-run effect when jobs change to update polling

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'in_progress': return 'text-blue-600';
      case 'pending': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">View your Documentation Jobs</h1>
      <div className="bg-white p-8 rounded-lg shadow-md">
        {loading && <LoadingSpinner />}
        {error && <ErrorMessage message={error} />}
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