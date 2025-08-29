import { Injectable } from '@nestjs/common';

@Injectable()
export class NotificationsService {
  getNotifications(userId: string) {
    return [{ id: 'notif1', userId, message: 'Welcome to the game!' }];
  }

  sendNotification(userId: string, message: string) {
    console.log(`Sending notification to ${userId}: ${message}`);
    return { id: 'new-notif', userId, message };
  }
}