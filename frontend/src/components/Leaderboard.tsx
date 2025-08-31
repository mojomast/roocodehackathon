import React from 'react';

const players = [
  { rank: 1, username: 'CYBER_PUNK_1', score: 10000 },
  { rank: 2, username: 'N3ON_K1NG', score: 9500 },
  { rank: 3, username: 'GLOW_QUEEN', score: 9000 },
  { rank: 4, username: 'V4P0R_W4V3', score: 8500 },
  { rank: 5, username: 'FUTURE_FUNK', score: 8000 },
];

const Leaderboard = () => {
  return (
    <div style={{
      background: '#141414',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 0 15px rgba(0, 191, 255, 0.5)',
      fontFamily: 'Exo 2, sans-serif',
      color: '#EAEAEA'
    }}>
      <h2 style={{ fontFamily: 'Orbitron, sans-serif', color: '#FFFFFF', marginBottom: '24px' }}>Top Players</h2>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {players.map((player, index) => (
          <li key={index} style={{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '12px 0',
            borderBottom: index < players.length - 1 ? '1px solid #2E2E2E' : 'none'
          }}>
            <span style={{ flex: '1', fontFamily: 'Orbitron, sans-serif' }}>{player.rank}</span>
            <span style={{ flex: '3' }}>{player.username}</span>
            <span style={{ flex: '1', textAlign: 'right', color: '#00BFFF' }}>{player.score}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Leaderboard;