import { Injectable } from '@nestjs/common';

@Injectable()
export class WebrtcService {
  handleSignal(signal: any) {
    console.log('Received WebRTC signal:', signal);
    return { message: 'Signal received and processed (dummy)' };
  }
}