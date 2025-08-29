import { Injectable } from '@nestjs/common';

@Injectable()
export class WalletService {
  getUserBalance(userId: string) {
    return { userId, balance: 1000 };
  }

  deposit(userId: string, amount: number) {
    console.log(`Depositing ${amount} for user ${userId}`);
    return { userId, newBalance: 1000 + amount };
  }

  withdraw(userId: string, amount: number) {
    console.log(`Withdrawing ${amount} for user ${userId}`);
    return { userId, newBalance: 1000 - amount };
  }
}