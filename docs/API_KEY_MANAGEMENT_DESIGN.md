# API Key Management Feature Design

## Introduction

This document outlines the technical design for a new feature that allows users to manage their API keys for various LLM services, such as OpenAI and Anthropic.

## Backend Design

### Database Model

A new table, `api_keys`, will be created to store the API keys.

```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    service VARCHAR(255) NOT NULL,
    encrypted_key TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Fields:**
- `id`: Primary key.
- `user_id`: Foreign key to the `users` table.
- `service`: The name of the service (e.g., "OPENAI", "ANTHROPIC").
- `encrypted_key`: The encrypted API key.
- `created_at`: Timestamp of when the key was added.
- `updated_at`: Timestamp of the last update.

### API Endpoints

The following RESTful endpoints will be created to manage API keys.

#### 1. Create API Key
- **Endpoint:** `POST /api/keys`
- **Description:** Adds a new API key for a user.
- **Request Body:**
  ```json
  {
    "service": "OPENAI",
    "api_key": "your_api_key_here"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "id": 1,
    "service": "OPENAI",
    "created_at": "2023-10-27T10:00:00Z"
  }
  ```

#### 2. Get API Keys
- **Endpoint:** `GET /api/keys`
- **Description:** Retrieves all API keys for the authenticated user.
- **Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "service": "OPENAI",
      "last_4_chars": "sk-...1234",
      "created_at": "2023-10-27T10:00:00Z"
    }
  ]
  ```

#### 3. Update API Key
- **Endpoint:** `PUT /api/keys/{key_id}`
- **Description:** Updates an existing API key.
- **Request Body:**
  ```json
  {
    "api_key": "your_new_api_key_here"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "id": 1,
    "service": "OPENAI",
    "updated_at": "2023-10-27T11:00:00Z"
  }
  ```

#### 4. Delete API Key
- **Endpoint:** `DELETE /api/keys/{key_id}`
- **Description:** Deletes an API key.
- **Response (204 No Content):** No response body.

### Security Considerations

- **Encryption at Rest:** API keys will be encrypted before being stored in the database. A symmetric encryption algorithm like AES-256-GCM will be used.
- **Encryption Key Management:** The encryption key will be stored securely, for example, in a dedicated secrets management service (e.g., AWS KMS, HashiCorp Vault) or as an environment variable. It will not be hardcoded in the application.
- **API Authentication:** All API endpoints for managing keys will require user authentication to ensure that users can only access their own keys.
- **Input Validation:** All user input will be validated to prevent injection attacks.
- **Masking:** API keys will be masked in the UI and in logs to prevent accidental exposure. Only the last 4 characters will be displayed.

## Frontend Design

### UI Components

- **API Key List:** A table or list that displays the user's API keys.
  - Each row will show the service name, the last 4 characters of the key, and the creation date.
  - Each row will have "Edit" and "Delete" buttons.
- **API Key Form:** A modal or separate page with a form to add or edit an API key.
  - **Service Dropdown:** A dropdown to select the service (e.g., "OpenAI", "Anthropic").
  - **API Key Input:** A text input for the API key.
  - **Save Button:** To submit the form.
- **Delete Confirmation:** A modal to confirm the deletion of an API key.

### User Flow

1.  The user navigates to the "Settings" page and clicks on "API Keys".
2.  The API Key Management page is displayed, showing a list of their existing keys.
3.  The user clicks the "Add New Key" button.
4.  The API Key Form appears.
5.  The user selects a service, enters their API key, and clicks "Save".
6.  The new key appears in the list, with the key value masked.
7.  To edit a key, the user clicks the "Edit" button, which opens the form with the existing data.
8.  To delete a key, the user clicks the "Delete" button and confirms the action in the confirmation modal.