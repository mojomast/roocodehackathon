# Game Site Monorepo

This monorepo contains the backend API, frontend application, and shared game modules for the Game Site platform.

## Table of Contents
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Overview](#api-overview)
- [Adding New Games](#adding-new-games)

## Setup Instructions

### Backend Setup

The backend is a NestJS application.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Run the application:**
    -   **Development mode:**
        ```bash
        npm run start:dev
        ```
    -   **Production mode:**
        ```bash
        npm run start:prod
        ```
    -   **Without watch mode:**
        ```bash
        npm run start
        ```
4.  **Run tests (optional):**
    -   **Unit tests:**
        ```bash
        npm run test
        ```
    -   **E2E tests:**
        ```bash
        npm run test:e2e
        ```
    -   **Test coverage:**
        ```bash
        npm run test:cov
        ```

### Frontend Setup

The frontend is a Next.js application.

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## API Overview

The backend API is built with NestJS and provides various endpoints for authentication, chat, games, leaderboards, notifications, user progress, store, user management, wallet, and WebRTC.

**Base URL:** `http://localhost:3000/api` (This can be configured in `games/api-hooks/game-api.ts`)

Here's a summary of the main API endpoints:

-   **Authentication (`/auth`)**
    -   `POST /auth/login`: User login.
    -   `POST /auth/register`: User registration.
    -   `GET /auth/profile`: Get authenticated user's profile.

-   **Chat (`/chat`)**
    -   `GET /chat/rooms`: Get available chat rooms.
    -   `GET /chat/rooms/:roomId/messages`: Get messages in a specific chat room.
    -   `POST /chat/rooms/:roomId/messages`: Post a message to a chat room.

-   **Games (`/games`)**
    -   `GET /games`: Get all available games.
    -   `GET /games/:id`: Get game details by ID.
    -   `POST /games/:id/sessions`: Create a new game session.
    -   `GET /games/:id/sessions`: Get game sessions for a specific game.

-   **Leaderboards (`/leaderboards`)**
    -   `GET /leaderboards/xp`: Get the XP leaderboard.

-   **Notifications (`/notifications`)**
    -   `GET /notifications/:userId`: Get notifications for a specific user.
    -   `POST /notifications/:userId/send`: Send a notification to a user.

-   **Progress (`/progress`)**
    -   `GET /progress/:userId`: Get user's progress.
    -   `POST /progress/:userId/xp`: Add XP to a user.
    -   `GET /progress/:userId/level`: Get user's level.

-   **Store (`/store`)**
    -   `GET /store/items`: Get all store items.
    -   `GET /store/items/:id`: Get store item by ID.
    -   `POST /store/purchase`: Purchase an item.

-   **Users (`/users`)**
    -   `GET /users`: Get all users.
    -   `GET /users/:id`: Get user by ID.
    -   `POST /users`: Create a new user.
    -   `PUT /users/:id`: Update user details.
    -   `DELETE /users/:id`: Delete a user.

-   **Wallet (`/wallet`)**
    -   `GET /wallet/:userId`: Get user's wallet balance.
    -   `POST /wallet/:userId/deposit`: Deposit funds into user's wallet.
    -   `POST /wallet/:userId/withdraw`: Withdraw funds from user's wallet.

-   **WebRTC (`/webrtc`)**
    -   `POST /webrtc/signal`: Handle WebRTC signaling.

## Adding New Games

To add a new game to the platform, you will primarily interact with the `games/GameTemplate` and `games/api-hooks/game-api.ts` modules.

### `games/GameTemplate/index.ts`

This file defines core interfaces and functions for integrating new games:

-   **`GameRegistrationData`**: Interface for data needed to register a new game (e.g., `gameId`, `gameName`, `description`).
-   **`GameSessionStartData`**: Interface for data to start a game session (e.g., `gameId`, `userId`).
-   **`GameScoreSubmissionData`**: Interface for submitting game scores and rewards (e.g., `sessionId`, `userId`, `score`, `rewards`).
-   **`ChatRoomAttachmentData`**: Interface for attaching a chat room to a game session.

**Key Functions:**

-   **`registerGame(data: GameRegistrationData)`**: Registers a new game with the backend. This would typically make an HTTP POST request to a `/games/register` endpoint (example provided in comments).
-   **`startGameSession(data: GameSessionStartData)`**: Creates and starts a new game session. This would typically make an HTTP POST request to a `/sessions/start` endpoint (example provided in comments).
-   **`submitGameScore(data: GameScoreSubmissionData)`**: Submits the score and rewards for a completed game session. This would typically make an HTTP POST request to a `/scores/submit` endpoint (example provided in comments).
-   **`attachChatRoomToSession(data: ChatRoomAttachmentData)`**: Attaches a chat room to an active game session. This would typically make an HTTP POST request to a `/chat/attach` endpoint (example provided in comments).

### `games/api-hooks/game-api.ts`

This file provides a centralized mechanism for games to interact with the backend API, abstracting away direct fetch/axios calls and handling authentication.

**Key Functions:**

-   **`setAuthToken(token: string | null)`**: Sets the authentication token for subsequent API requests.
-   **`register(username: string, password: string)`**: Registers a new user.
-   **`login(username: string, password: string)`**: Logs in an existing user and obtains an authentication token.
-   **`logout()`**: Logs out the current user by clearing the authentication token.
-   **`startGameSession(gameId: string)`**: Initiates a new game session.
-   **`submitGameResult(sessionId: string, score: number, otherGameData: any)`**: Submits the result of a game session.
-   **`getUserProfile()`**: Retrieves the profile of the currently authenticated user.
-   **`getWallet()`**: Retrieves the wallet information for the currently authenticated user.
-   **`updateUserProfile(profileData: any)`**: Updates the user's profile information.

**How to add a new game:**

1.  **Define your game logic:** Create your game's core logic and UI.
2.  **Register your game:** Use the `registerGame` function from `games/GameTemplate/index.ts` to register your game with the backend, providing its `gameId`, `gameName`, and `description`.
3.  **Manage game sessions:**
    -   When a user starts playing, use `startGameSession` from `games/GameTemplate/index.ts` to create a new session.
    -   When the game ends, use `submitGameScore` from `games/GameTemplate/index.ts` to submit the score and any rewards.
4.  **Utilize API hooks:** For any other backend interactions (e.g., user authentication, fetching user profile, managing wallet, chat), use the functions provided in `games/api-hooks/game-api.ts`. These functions handle authentication and simplify API calls.
5.  **Integrate with chat (optional):** If your game requires in-game chat, use `attachChatRoomToSession` from `games/GameTemplate/index.ts` to link a chat room to your game session.