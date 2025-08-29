import { Controller, Get } from '@nestjs/common';
import { LeaderboardsService } from './leaderboards.service';

@Controller('leaderboards')
export class LeaderboardsController {
  constructor(private readonly leaderboardsService: LeaderboardsService) {}

  @Get('xp')
  getXpLeaderboard() {
    return this.leaderboardsService.getXpLeaderboard();
  }
}