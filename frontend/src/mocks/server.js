// frontend/src/mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Set up MSW server with the handlers
export const server = setupServer(...handlers);