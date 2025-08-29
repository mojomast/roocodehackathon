import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { ProgressModule } from './progress/progress.module';
import { LeaderboardsModule } from './leaderboards/leaderboards.module';
import { WalletModule } from './wallet/wallet.module';
import { StoreModule } from './store/store.module';
import { ChatModule } from './chat/chat.module';
import { GamesModule } from './games/games.module';
import { WebrtcModule } from './webrtc/webrtc.module';
import { NotificationsModule } from './notifications/notifications.module';
import { EventsGateway } from './events/events.gateway';

@Module({
  imports: [
    AuthModule,
    UsersModule,
    ProgressModule,
    LeaderboardsModule,
    WalletModule,
    StoreModule,
    ChatModule,
    GamesModule,
    WebrtcModule,
    NotificationsModule,
  ],
  controllers: [AppController],
  providers: [AppService, EventsGateway],
})
export class AppModule {}
