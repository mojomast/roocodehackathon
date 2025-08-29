import { Controller, Get, Param, Post, Body } from '@nestjs/common';
import { WalletService } from './wallet.service';

@Controller('wallet')
export class WalletController {
  constructor(private readonly walletService: WalletService) {}

  @Get(':userId')
  getUserBalance(@Param('userId') userId: string) {
    return this.walletService.getUserBalance(userId);
  }

  @Post(':userId/deposit')
  deposit(@Param('userId') userId: string, @Body('amount') amount: number) {
    return this.walletService.deposit(userId, amount);
  }

  @Post(':userId/withdraw')
  withdraw(@Param('userId') userId: string, @Body('amount') amount: number) {
    return this.walletService.withdraw(userId, amount);
  }
}