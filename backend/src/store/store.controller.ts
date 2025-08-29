import { Controller, Get, Param, Post, Body } from '@nestjs/common';
import { StoreService } from './store.service';

@Controller('store')
export class StoreController {
  constructor(private readonly storeService: StoreService) {}

  @Get('items')
  getAllItems() {
    return this.storeService.getAllItems();
  }

  @Get('items/:id')
  getItemById(@Param('id') id: string) {
    return this.storeService.getItemById(id);
  }

  @Post('purchase')
  purchaseItem(@Body('userId') userId: string, @Body('itemId') itemId: string) {
    return this.storeService.purchaseItem(userId, itemId);
  }
}