import { Controller, Post, Body } from '@nestjs/common';
import { WebrtcService } from './webrtc.service';

@Controller('webrtc')
export class WebrtcController {
  constructor(private readonly webrtcService: WebrtcService) {}

  @Post('signal')
  handleSignal(@Body() signal: any) {
    return this.webrtcService.handleSignal(signal);
  }
}