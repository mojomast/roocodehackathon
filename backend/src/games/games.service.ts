import { Injectable } from '@nestjs/common';
import { ProgressService } from '../progress/progress.service';
import { WalletService } from '../wallet/wallet.service';

@Injectable()
export class GamesService {
  constructor(
    private readonly progressService: ProgressService,
    private readonly walletService: WalletService,
  ) {}

  getAllGames() {
    return [{ id: 'game1', name: 'Awesome Game' }, { id: 'game2', name: 'Another Game' }];
  }

  getGameById(id: string) {
    return { id, name: `Game ${id}` };
  }

  createGameSession(gameId: string, userId: string) {
    console.log(`Creating session for game ${gameId} by user ${userId}`);
    return { sessionId: 'session123', gameId, userId, status: 'created' };
  }

  getGameSessions(gameId: string) {
    return [{ sessionId: 'session123', gameId, userId: 'user1', status: 'active' }];
  }

  async submitScore(
    gameId: string,
    userId: string,
    score: number,
    xpEarned: number,
    currencyEarned: number,
  ) {
    console.log(`Submitting score for game ${gameId} by user ${userId}: Score ${score}, XP ${xpEarned}, Currency ${currencyEarned}`);

    // Award XP
    const updatedProgress = await this.progressService.addXp(userId, xpEarned);

    // Award currency
    const updatedWallet = await this.walletService.deposit(userId, currencyEarned);

    return {
      message: 'Score submitted successfully',
      userId,
      gameId,
      score,
      xpEarned,
      currencyEarned,
      updatedProgress,
      updatedWallet,
    };
  }
}