import { WebSocketGateway, SubscribeMessage, WebSocketServer, ConnectedSocket, MessageBody } from '@nestjs/websockets';
import { OnGatewayConnection, OnGatewayDisconnect, OnGatewayInit } from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';

@WebSocketGateway({
  cors: {
    origin: '*',
  },
})
export class EventsGateway implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer() server: Server;

  afterInit(server: Server) {
    console.log('WebSocket Gateway initialized');
  }

  handleConnection(client: Socket, ...args: any[]) {
    console.log(`Client connected: ${client.id}`);
  }

  handleDisconnect(client: Socket) {
    console.log(`Client disconnected: ${client.id}`);
  }

  @SubscribeMessage('message')
  handleMessage(@MessageBody() data: string, @ConnectedSocket() client: Socket): void {
    this.server.emit('message', data);
  }

  @SubscribeMessage('joinRoom')
  handleJoinRoom(@MessageBody() room: string, @ConnectedSocket() client: Socket): void {
    client.join(room);
    client.emit('joinedRoom', room);
  }

  @SubscribeMessage('leaveRoom')
  handleLeaveRoom(@MessageBody() room: string, @ConnectedSocket() client: Socket): void {
    client.leave(room);
    client.emit('leftRoom', room);
  }

  @SubscribeMessage('gameUpdate')
  handleGameUpdate(@MessageBody() data: any): void {
    this.server.emit('gameUpdate', data);
  }

  @SubscribeMessage('gameStart')
  handleGameStart(@MessageBody() data: any): void {
    this.server.emit('gameStart', data);
  }

  @SubscribeMessage('gameEnd')
  handleGameEnd(@MessageBody() data: any): void {
    this.server.emit('gameEnd', data);
  }
}