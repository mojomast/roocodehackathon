# FixMyDocs

FixMyDocs is a comprehensive application designed to streamline documentation processes. It provides a robust platform for managing, updating, and maintaining project documentation, ensuring accuracy and accessibility.

## Getting Started

Follow these steps to set up and run the FixMyDocs application locally:

1.  **Create `.env` files:**
    For each service (backend, frontend, worker), create a `.env` file by copying its respective `.env.template` file.
    -   `cp backend/.env.template backend/.env`
    -   `cp frontend/.env.template frontend/.env`
    -   `cp worker/.env.template worker/.env`

2.  **Build and Run with Docker Compose:**
    Navigate to the root directory of the project and execute the following command to build and start all services:
    ```bash
    docker-compose up --build
    ```

3.  **Access the Frontend:**
    Once the services are up and running, you can access the frontend application in your web browser at:
    `http://localhost:3000`