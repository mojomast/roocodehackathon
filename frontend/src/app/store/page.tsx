import React from 'react';
import StoreItem from '@/components/StoreItem';

const StorePage = () => {
  const items = [
    { name: 'Cybernetic Arm', price: 'Ƀ 1.2', imageUrl: 'IMAGE' },
    { name: 'Neural Interface', price: 'Ƀ 2.5', imageUrl: 'IMAGE' },
    { name: 'Plasma Rifle', price: 'Ƀ 3.0', imageUrl: 'IMAGE' },
    { name: 'Stealth Cloak', price: 'Ƀ 1.8', imageUrl: 'IMAGE' },
    { name: 'Anti-Grav Boots', price: 'Ƀ 0.9', imageUrl: 'IMAGE' },
    { name: 'AI Companion', price: 'Ƀ 5.0', imageUrl: 'IMAGE' },
  ];

  return (
    <div className="p-8">
      <h1 className="text-4xl font-orbitron text-white mb-8">Cyber Store</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {items.map((item, index) => (
          <StoreItem key={index} name={item.name} price={item.price} imageUrl={item.imageUrl} />
        ))}
      </div>
    </div>
  );
};

export default StorePage;