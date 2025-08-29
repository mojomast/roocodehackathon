import { Controller, Get, Param, Post, Body } from '@nestjs/common';
import { NotificationsService } from './notifications.service';

@Controller('notifications')
export class NotificationsController {
  constructor(private readonly notificationsService: NotificationsService) {}

  @Get(':userId')
  getNotifications(@Param('userId') userId: string) {
    return this.notificationsService.getNotifications(userId);
  }

  @Post(':userId/send')
  sendNotification(@Param('userId') userId: string, @Body('message') message: string) {
    return this.notificationsService.sendNotification(userId, message);
  }
}