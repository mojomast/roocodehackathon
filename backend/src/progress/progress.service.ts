import { Injectable } from '@nestjs/common';

@Injectable()
export class ProgressService {
  getUserProgress(userId: string) {
    return { userId, xp: 100, level: 1 };
  }

  addXp(userId: string, amount: number) {
    console.log(`Adding ${amount} XP to user ${userId}`);
    return { userId, xp: 100 + amount, level: 1 };
  }

  getUserLevel(userId: string) {
    return { userId, level: 1 };
  }
}