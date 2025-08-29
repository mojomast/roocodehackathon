import { Controller, Get, Param, Post, Body } from '@nestjs/common';
import { ProgressService } from './progress.service';

@Controller('progress')
export class ProgressController {
  constructor(private readonly progressService: ProgressService) {}

  @Get(':userId')
  getUserProgress(@Param('userId') userId: string) {
    return this.progressService.getUserProgress(userId);
  }

  @Post(':userId/xp')
  addXp(@Param('userId') userId: string, @Body('amount') amount: number) {
    return this.progressService.addXp(userId, amount);
  }

  @Get(':userId/level')
  getUserLevel(@Param('userId') userId: string) {
    return this.progressService.getUserLevel(userId);
  }
}