# FixMyDocs Project

This project aims to provide a comprehensive solution for managing and fixing documentation.

## Setup Instructions

### Using Docker Compose

To get the project up and running quickly using Docker Compose, follow these steps:

1.  **Ensure Docker is installed:** Make sure you have Docker and Docker Compose installed on your system.
2.  **Build and run the services:** Navigate to the root directory of the project and execute the following command:
    ```bash
    docker-compose up --build
    ```
    This command will build the necessary Docker images and start all defined services (frontend, backend, worker).

### Services Overview

The project consists of the following services:

*   **Frontend:** A Next.js application serving the user interface.
*   **Backend:** A Python Flask application providing API endpoints.
*   **Worker:** A Python application handling background tasks.
