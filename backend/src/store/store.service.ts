import { Injectable } from '@nestjs/common';
import { WalletService } from '../wallet/wallet.service';

@Injectable()
export class StoreService {
  constructor(private readonly walletService: WalletService) {}

  getAllItems() {
    return [
      { id: 'item1', name: 'Sword of Awesomeness', price: 100 },
      { id: 'item2', name: 'Shield of Defense', price: 50 },
    ];
  }

  getItemById(id: string) {
    return { id, name: `Item ${id}`, price: 100 };
  }

  async purchaseItem(userId: string, itemId: string) {
    console.log(`User ${userId} purchasing item ${itemId}`);
    const item = this.getItemById(itemId); // In a real app, fetch from DB
    if (!item) {
      throw new Error('Item not found');
    }
    await this.walletService.withdraw(userId, item.price);
    return { message: `Item ${itemId} purchased by ${userId}`, userId, itemId, price: item.price };
  }
}