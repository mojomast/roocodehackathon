import React from 'react';

interface StoreItemProps {
  name: string;
  price: string;
  imageUrl: string;
}

const StoreItem: React.FC<StoreItemProps> = ({ name, price, imageUrl }) => {
  return (
    <div className="bg-[#141414] rounded-lg p-4 flex flex-col items-center text-white font-orbitron border border-[#2E2E2E] hover:border-[#9400FF] hover:shadow-[0_0_15px_#9400FF] transition-all duration-200 ease-out">
      <div className="w-full h-48 bg-gray-700 rounded-md mb-4 flex items-center justify-center">
        <span className="text-gray-400">{imageUrl}</span>
      </div>
      <h3 className="text-lg font-bold">{name}</h3>
      <p className="text-[#39FF14] mb-4">{price}</p>
      <button className="btn-cyber">
        Buy
      </button>
    </div>
  );
};

export default StoreItem;