// games/api-hooks/game-api.ts

/**
 * @file This file provides a centralized mechanism for games to interact with the backend API.
 * It abstracts away direct fetch/axios calls and handles authentication.
 */

// Configuration for the backend API. In a real application, BASE_URL and AUTH_TOKEN
// would typically be managed via environment variables or a global state/context.
const BASE_URL = 'http://localhost:3000/api'; // Example base URL for the backend API
let AUTH_TOKEN: string | null = null; // Placeholder for the authentication token

/**
 * Sets the authentication token for subsequent API requests.
 * @param token The authentication token received after login or registration.
 */
export const setAuthToken = (token: string | null): void => {
  AUTH_TOKEN = token;
};

/**
 * Helper function to make authenticated API requests.
 * @param endpoint The API endpoint to call (e.g., '/auth/login').
 * @param method The HTTP method (e.g., 'GET', 'POST').
 * @param data Optional data to send with the request (for POST, PUT).
 * @returns A promise that resolves with the JSON response from the API.
 * @throws An error if the network request fails or the API returns an error.
 */
async function authenticatedRequest<T>(
  endpoint: string,
  method: string,
  data?: any
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }

  const config: RequestInit = {
    method,
    headers,
    body: data ? JSON.stringify(data) : undefined,
  };

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `API Error: ${response.statusText}`);
    }

    return response.json();
  } catch (error) {
    console.error(`Error making request to ${endpoint}:`, error);
    throw error;
  }
}

// --- Authentication Endpoints ---

/**
 * Registers a new user with the backend.
 * @param username The desired username.
 * @param password The user's password.
 * @returns A promise that resolves with the registration response (e.g., user data, token).
 */
interface AuthResponse {
  token?: string;
  // Add other properties that your auth response might include, e.g., user: UserProfile;
}

export const register = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await authenticatedRequest<AuthResponse>('/auth/register', 'POST', { username, password });
  // Assuming the registration response includes a token, set it for future requests.
  if (response.token) {
    setAuthToken(response.token);
  }
  return response;
};

/**
 * Logs in an existing user and obtains an authentication token.
 * @param username The user's username.
 * @param password The user's password.
 * @returns A promise that resolves with the login response (e.g., user data, token).
 */
export const login = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await authenticatedRequest<AuthResponse>('/auth/login', 'POST', { username, password });
  // Assuming the login response includes a token, set it for future requests.
  if (response.token) {
    setAuthToken(response.token);
  }
  return response;
};

/**
 * Logs out the current user by clearing the authentication token.
 */
export const logout = (): void => {
  setAuthToken(null);
  console.log('User logged out. Token cleared.');
};

// --- Game-Related Endpoints ---

/**
 * Initiates a new game session.
 * @param gameId The ID of the game to start.
 * @returns A promise that resolves with the new game session details.
 */
export const startGameSession = async (gameId: string): Promise<any> => {
  return authenticatedRequest(`/games/${gameId}/start`, 'POST');
};

/**
 * Submits the result of a game session.
 * @param sessionId The ID of the game session.
 * @param score The player's score in the game.
 * @param otherGameData Any other relevant game data to submit.
 * @returns A promise that resolves with the submission confirmation.
 */
export const submitGameResult = async (
  sessionId: string,
  score: number,
  otherGameData: any
): Promise<any> => {
  return authenticatedRequest(`/games/${sessionId}/submit-result`, 'POST', { score, otherGameData });
};

// --- User-Related Endpoints ---

/**
 * Retrieves the profile of the currently authenticated user.
 * Requires an authentication token to be set.
 * @returns A promise that resolves with the user's profile data.
 */
export const getUserProfile = async (): Promise<any> => {
  return authenticatedRequest('/users/profile', 'GET');
};

/**
 * Retrieves the wallet information for the currently authenticated user.
 * Requires an authentication token to be set.
 * @returns A promise that resolves with the user's wallet data.
 */
export const getWallet = async (): Promise<any> => {
  return authenticatedRequest('/wallet', 'GET');
};

/**
 * Updates the user's profile information.
 * @param profileData The data to update in the user's profile.
 * @returns A promise that resolves with the updated user profile.
 */
export const updateUserProfile = async (profileData: any): Promise<any> => {
  return authenticatedRequest('/users/profile', 'PUT', profileData);
};