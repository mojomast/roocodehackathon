"use client";

import { useParams } from "next/navigation";

export default function GamePlaceholder() {
  const params = useParams();
  const gameId = params.id;

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Game Placeholder Page</h1>
      <p className="mb-4">
        This page demonstrates how a game hooks into the API.
      </p>
      <p className="mb-4">
        Game ID from route parameter: <strong>{gameId}</strong>
      </p>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">API Integration Notes</h2>
        <ul>
          <li>[Placeholder for game session start via API]</li>
          <li>[Placeholder for sending game results (XP, score, currency) to backend]</li>
          <li>[Placeholder for accessing leaderboard]</li>
          <li>[Placeholder for accessing session chat]</li>
        </ul>
      </section>
    </div>
  );
}