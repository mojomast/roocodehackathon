import React from 'react';

interface GlowingCardProps {
  children: React.ReactNode;
  title: string;
  className?: string;
}

const GlowingCard: React.FC<GlowingCardProps> = ({ children, title, className }) => {
  return (
    <div
      className={className}
      style={{
        background: '#141414',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 0 15px rgba(0, 191, 255, 0.5)',
        fontFamily: 'Exo 2, sans-serif',
        color: '#EAEAEA',
        marginBottom: '2rem'
      }}
    >
      <h2 style={{ fontFamily: 'Orbitron, sans-serif', color: '#FFFFFF', marginBottom: '24px', fontSize: '1.5rem' }}>{title}</h2>
      {children}
    </div>
  );
};

export default GlowingCard;