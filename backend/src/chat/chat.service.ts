import { Injectable } from '@nestjs/common';

@Injectable()
export class ChatService {
  getChatRooms() {
    return [{ id: 'general', name: 'General Chat' }, { id: 'gaming', name: 'Gaming Lounge' }];
  }

  getMessagesInRoom(roomId: string) {
    return [{ id: 'msg1', userId: 'user1', message: `Hello from ${roomId}` }];
  }

  postMessage(roomId: string, userId: string, message: string) {
    console.log(`User ${userId} posted "${message}" in room ${roomId}`);
    return { id: 'new-msg', roomId, userId, message };
  }
}