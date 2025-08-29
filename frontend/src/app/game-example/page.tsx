"use client";

import { useEffect, useState } from 'react';
import { useSocket } from '../../../src/context/SocketContext';
import { useRouter } from 'next/navigation';

export default function GameIntegrationExample() {
  const socket = useSocket();
  const [messages, setMessages] = useState<string[]>([]);
  const [userId, setUserId] = useState<string | null>(null);
  const [userXp, setUserXp] = useState<number>(0);
  const [userCurrency, setUserCurrency] = useState<number>(0);
  const router = useRouter();

  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    if (!storedUserId) {
      router.push('/'); // Redirect to login if not authenticated
      return;
    }
    setUserId(storedUserId);
    fetchUserData(storedUserId);

    if (!socket) return;

    socket.on('connect', () => {
      setMessages((prev) => [...prev, 'Connected to Socket.IO server!']);
    });

    socket.on('disconnect', () => {
      setMessages((prev) => [...prev, 'Disconnected from Socket.IO server.']);
    });

    socket.on('gameUpdate', (message: string) => {
      setMessages((prev) => [...prev, `Game Update: ${message}`]);
    });

    socket.on('chatMessage', (message: string) => {
      setMessages((prev) => [...prev, `Chat Message: ${message}`]);
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('gameUpdate');
      socket.off('chatMessage');
    };
  }, [socket, router]);

  const fetchUserData = async (id: string) => {
    try {
      const xpResponse = await fetch(`http://localhost:3000/progress/${id}`);
      const xpData = await xpResponse.json();
      setUserXp(xpData.xp);

      const walletResponse = await fetch(`http://localhost:3000/wallet/${id}`);
      const walletData = await walletResponse.json();
      setUserCurrency(walletData.balance);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const handleStartGameSession = async () => {
    if (!userId) {
      alert('Please log in first.');
      return;
    }
    try {
      const gameId = 'game1'; // Example game ID
      const response = await fetch(`http://localhost:3000/games/${gameId}/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId }),
      });
      const data = await response.json();
      if (response.ok) {
        setMessages((prev) => [...prev, `Game session started: ${JSON.stringify(data)}`]);
      } else {
        setMessages((prev) => [...prev, `Failed to start game session: ${data.message || response.statusText}`]);
      }
    } catch (error) {
      setMessages((prev) => [...prev, `Error starting game session: ${error}`]);
      console.error('Error starting game session:', error);
    }
  };

  const handleSubmitScore = async () => {
    if (!userId) {
      alert('Please log in first.');
      return;
    }
    try {
      const gameId = 'game1'; // Example game ID
      const score = Math.floor(Math.random() * 1000);
      const xpEarned = Math.floor(Math.random() * 50) + 10;
      const currencyEarned = Math.floor(Math.random() * 20) + 5;

      const response = await fetch(`http://localhost:3000/games/${gameId}/submit-score`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId, score, xpEarned, currencyEarned }),
      });
      const data = await response.json();
      if (response.ok) {
        setMessages((prev) => [...prev, `Score submitted: ${JSON.stringify(data)}`]);
        fetchUserData(userId); // Refresh user data
      } else {
        setMessages((prev) => [...prev, `Failed to submit score: ${data.message || response.statusText}`]);
      }
    } catch (error) {
      setMessages((prev) => [...prev, `Error submitting score: ${error}`]);
      console.error('Error submitting score:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userId');
    router.push('/');
  };

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Game Integration Example Page</h1>
      <button
        onClick={handleLogout}
        className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded absolute top-4 right-4"
      >
        Logout
      </button>
      <p className="mb-4">
        This page demonstrates how a mini-game integrates with the backend API.
      </p>
      {userId && (
        <div className="mb-4 text-lg">
          <p>User ID: {userId}</p>
          <p>XP: {userXp}</p>
          <p>Currency: {userCurrency}</p>
        </div>
      )}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Mini-Game Stub (e.g., Clicker or Trivia)</h2>
        <p>[Placeholder for a simple mini-game UI]</p>
        <button
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mt-4 mr-4"
          onClick={handleStartGameSession}
        >
          Start Game Session
        </button>
        <button
          className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded mt-4"
          onClick={handleSubmitScore}
        >
          Submit Score
        </button>
      </section>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Socket.IO Messages</h2>
        <div className="bg-gray-800 p-4 rounded h-48 overflow-y-auto">
          {messages.map((msg, index) => (
            <p key={index} className="text-gray-300 text-sm">{msg}</p>
          ))}
        </div>
      </section>
    </div>
  );
}