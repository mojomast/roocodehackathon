"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Store() {
  const [userId, setUserId] = useState<string | null>(null);
  const [userCurrency, setUserCurrency] = useState<number>(0);
  const [message, setMessage] = useState<string>('');
  const router = useRouter();

  const storeItems = [
    { id: 'item1', name: 'Health Potion', price: 50 },
    { id: 'item2', name: 'Mana Potion', price: 75 },
    { id: 'item3', name: 'Super Sword', price: 500 },
  ];

  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    if (!storedUserId) {
      router.push('/'); // Redirect to login if not authenticated
      return;
    }
    setUserId(storedUserId);
    fetchUserCurrency(storedUserId);
  }, [router]);

  const fetchUserCurrency = async (id: string) => {
    try {
      const walletResponse = await fetch(`http://localhost:3000/wallet/${id}`);
      const walletData = await walletResponse.json();
      setUserCurrency(walletData.balance);
    } catch (error) {
      console.error('Failed to fetch user currency:', error);
      setMessage('Failed to fetch user currency.');
    }
  };

  const handlePurchaseItem = async (itemId: string, itemPrice: number) => {
    if (!userId) {
      alert('Please log in first.');
      return;
    }
    if (userCurrency < itemPrice) {
      setMessage('Not enough currency to purchase this item.');
      return;
    }

    try {
      const response = await fetch('http://localhost:3000/store/purchase', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId, itemId }),
      });
      const data = await response.json();
      if (response.ok) {
        setMessage(`Successfully purchased ${data.itemId}!`);
        fetchUserCurrency(userId); // Refresh currency
      } else {
        setMessage(data.message || 'Purchase failed.');
      }
    } catch (error) {
      setMessage('An error occurred during purchase.');
      console.error('Purchase error:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userId');
    router.push('/');
  };

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Store Page</h1>
      <button
        onClick={handleLogout}
        className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded absolute top-4 right-4"
      >
        Logout
      </button>
      {userId && (
        <div className="mb-4 text-lg">
          <p>User ID: {userId}</p>
          <p>Your Currency: {userCurrency}</p>
        </div>
      )}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Cosmetics Marketplace</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {storeItems.map((item) => (
            <div key={item.id} className="bg-white p-4 rounded shadow-md">
              <h3 className="text-xl font-bold mb-2">{item.name}</h3>
              <p className="text-gray-700 mb-4">Price: {item.price} currency</p>
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                onClick={() => handlePurchaseItem(item.id, item.price)}
              >
                Purchase Item
              </button>
            </div>
          ))}
        </div>
        {message && <p className="mt-4 text-center text-sm text-gray-600">{message}</p>}
      </section>
    </div>
  );
}