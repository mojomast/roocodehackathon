import React from 'react';

const ProfileCard = () => {
  return (
    <div style={{
      backgroundColor: '#141414',
      borderRadius: '16px',
      padding: '24px',
      textAlign: 'center',
      boxShadow: '0 0 15px 5px rgba(0, 191, 255, 0.5)',
      border: '1px solid #2E2E2E'
    }}>
      <div style={{
        width: '100px',
        height: '100px',
        borderRadius: '50%',
        backgroundColor: '#2E2E2E',
        margin: '0 auto 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '12px'
      }}>
        Avatar
      </div>
      <h2 style={{
        fontFamily: 'Orbitron, sans-serif',
        color: '#FFFFFF',
        margin: '0 0 8px'
      }}>
        Username
      </h2>
      <p style={{
        fontFamily: 'Exo 2, sans-serif',
        color: '#00BFFF',
        margin: '0 0 24px'
      }}>
        Rank: Diamond
      </p>
      <div style={{
        display: 'flex',
        justifyContent: 'space-around',
        fontFamily: 'Exo 2, sans-serif',
        color: '#EAEAEA'
      }}>
        <div>
          <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>1,234</p>
          <p style={{ margin: 0, fontSize: '12px' }}>Kills</p>
        </div>
        <div>
          <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>567</p>
          <p style={{ margin: 0, fontSize: '12px' }}>Wins</p>
        </div>
        <div>
          <p style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>890</p>
          <p style={{ margin: 0, fontSize: '12px' }}>Matches</p>
        </div>
      </div>
    </div>
  );
};

export default ProfileCard;