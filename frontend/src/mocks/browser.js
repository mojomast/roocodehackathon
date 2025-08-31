// frontend/src/mocks/browser.js
import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

// Set up MSW worker for the browser
export const worker = setupWorker(...handlers);