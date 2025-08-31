'use client';

import React, { useState, useEffect } from 'react';
import { apiClient, APIError, ApiKey } from '../../utils/apiClient';

const ApiKeyManagementPage = () => {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [service, setService] = useState('OPENAI');
  const [apiKey, setApiKey] = useState('');
  const [editingKey, setEditingKey] = useState<ApiKey | null>(null);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      setLoading(true);
      const keys = await apiClient.getApiKeys();
      setApiKeys(keys);
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingKey) {
        await apiClient.updateApiKey(editingKey.id, { api_key: apiKey });
      } else {
        await apiClient.createApiKey({ service, api_key: apiKey });
      }
      setService('OPENAI');
      setApiKey('');
      setShowForm(false);
      setEditingKey(null);
      fetchApiKeys();
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'An unexpected error occurred.');
    }
  };

  const handleEdit = (key: ApiKey) => {
    setEditingKey(key);
    setService(key.service);
    setApiKey('');
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this API key?')) {
      try {
        await apiClient.deleteApiKey(id);
        fetchApiKeys();
      } catch (err) {
        setError(err instanceof APIError ? err.message : 'An unexpected error occurred.');
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">API Key Management</h1>

      {error && <p className="text-red-500">{error}</p>}

      <button
        onClick={() => {
          setShowForm(!showForm);
          setEditingKey(null);
          setService('OPENAI');
          setApiKey('');
        }}
        className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
      >
        {showForm ? 'Cancel' : 'Add New Key'}
      </button>

      {showForm && (
        <form onSubmit={handleFormSubmit} className="mb-4 p-4 border rounded">
          <h2 className="text-xl font-bold mb-2">{editingKey ? 'Edit' : 'Add'} API Key</h2>
          <div className="mb-2">
            <label htmlFor="service" className="block">Service</label>
            <select
              id="service"
              value={service}
              onChange={(e) => setService(e.target.value)}
              className="w-full p-2 border rounded"
              disabled={!!editingKey}
            >
              <option value="OPENAI">OpenAI</option>
              <option value="ANTHROPIC">Anthropic</option>
            </select>
          </div>
          <div className="mb-2">
            <label htmlFor="apiKey" className="block">API Key</label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder={editingKey ? 'Enter new key' : 'Enter key'}
            />
          </div>
          <button type="submit" className="bg-green-500 text-white px-4 py-2 rounded">
            Save
          </button>
        </form>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2">Service</th>
              <th className="py-2">Key (Last 4)</th>
              <th className="py-2">Created At</th>
              <th className="py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {apiKeys.map((key) => (
              <tr key={key.id}>
                <td className="border px-4 py-2">{key.service}</td>
                <td className="border px-4 py-2">{key.last_4_chars}</td>
                <td className="border px-4 py-2">{new Date(key.created_at).toLocaleString()}</td>
                <td className="border px-4 py-2">
                  <button onClick={() => handleEdit(key)} className="bg-yellow-500 text-white px-2 py-1 rounded mr-2">
                    Edit
                  </button>
                  <button onClick={() => handleDelete(key.id)} className="bg-red-500 text-white px-2 py-1 rounded">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ApiKeyManagementPage;