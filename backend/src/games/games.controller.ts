import { Controller, Get, Param, Post, Body } from '@nestjs/common';
import { GamesService } from './games.service';

@Controller('games')
export class GamesController {
  constructor(private readonly gamesService: GamesService) {}

  @Get()
  getAllGames() {
    return this.gamesService.getAllGames();
  }

  @Get(':id')
  getGameById(@Param('id') id: string) {
    return this.gamesService.getGameById(id);
  }

  @Post(':id/sessions')
  createGameSession(@Param('id') gameId: string, @Body('userId') userId: string) {
    return this.gamesService.createGameSession(gameId, userId);
  }

  @Get(':id/sessions')
  getGameSessions(@Param('id') gameId: string) {
    return this.gamesService.getGameSessions(gameId);
  }

  @Post(':id/submit-score')
  submitScore(
    @Param('id') gameId: string,
    @Body('userId') userId: string,
    @Body('score') score: number,
    @Body('xpEarned') xpEarned: number,
    @Body('currencyEarned') currencyEarned: number,
  ) {
    return this.gamesService.submitScore(gameId, userId, score, xpEarned, currencyEarned);
  }
}