import '@testing-library/jest-dom';

// Import fetch polyfill for jsdom environment
import 'jest-fetch-mock';

// MSW setup for API mocking
import { server } from './src/mocks/server';

// Mock localStorage and sessionStorage for testing
const localStorageMock = () => {
  let storage = {};

  return {
    getItem: key => storage[key],
    setItem: (key, value) => storage[key] = value.toString(),
    removeItem: key => delete storage[key],
    clear: () => storage = {},
  };
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock()
});

Object.defineProperty(window, 'sessionStorage', {
  value: localStorageMock()
});

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests
afterEach(() => {
  server.resetHandlers();
  // Clear all mocks after each test
  jest.clearAllMocks();
});

// Clean up after all tests are done
afterAll(() => server.close());

// Mock timers for time-sensitive tests
jest.useFakeTimers();

// Mock crypto for security-related tests
const cryptoMock = {
  getRandomValues: (array) => {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256);
    }
    return array;
  }
};

Object.defineProperty(window, 'crypto', {
  value: cryptoMock
});

// Mock matchMedia for responsive component testing
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});