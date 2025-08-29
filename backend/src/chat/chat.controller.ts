import { Controller, Get, Param, Post, Body } from '@nestjs/common';
import { ChatService } from './chat.service';

@Controller('chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Get('rooms')
  getChatRooms() {
    return this.chatService.getChatRooms();
  }

  @Get('rooms/:roomId/messages')
  getMessagesInRoom(@Param('roomId') roomId: string) {
    return this.chatService.getMessagesInRoom(roomId);
  }

  @Post('rooms/:roomId/messages')
  postMessage(
    @Param('roomId') roomId: string,
    @Body('userId') userId: string,
    @Body('message') message: string,
  ) {
    return this.chatService.postMessage(roomId, userId, message);
  }
}