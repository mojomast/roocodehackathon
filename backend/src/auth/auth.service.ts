import { Injectable } from '@nestjs/common';

@Injectable()
export class AuthService {
  login(body: any) {
    console.log('Login attempt:', body);
    // For demonstration, return a dummy token and user ID
    return { accessToken: 'dummy-access-token', userId: 'dummy-user-id' };
  }

  register(body: any) {
    console.log('Registration attempt:', body);
    return { message: 'Registration successful (dummy)' };
  }

  getProfile() {
    return { userId: 'dummy-user-id', username: 'dummy-username' };
  }
}