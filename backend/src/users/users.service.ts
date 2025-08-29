import { Injectable } from '@nestjs/common';

@Injectable()
export class UsersService {
  findAll() {
    return [{ id: '1', name: 'Dummy User 1' }, { id: '2', name: 'Dummy User 2' }];
  }

  findOne(id: string) {
    return { id, name: `Dummy User ${id}` };
  }

  create(body: any) {
    console.log('Creating user:', body);
    return { id: 'new-id', ...body };
  }

  update(id: string, body: any) {
    console.log(`Updating user ${id}:`, body);
    return { id, ...body };
  }

  remove(id: string) {
    console.log(`Removing user ${id}`);
    return { message: `User ${id} removed` };
  }
}