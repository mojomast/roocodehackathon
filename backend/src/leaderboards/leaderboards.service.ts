import { Injectable } from '@nestjs/common';

@Injectable()
export class LeaderboardsService {
  getXpLeaderboard() {
    return [
      { userId: 'user1', username: 'PlayerA', xp: 1000 },
      { userId: 'user2', username: 'PlayerB', xp: 900 },
      { userId: 'user3', username: 'PlayerC', xp: 800 },
    ];
  }
}