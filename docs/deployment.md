# EthosMCP Deployment Guide

This guide provides instructions for deploying the EthosMCP server using Docker and Docker Compose.

## 1. Prerequisites

*   Docker Engine (version 20.10.0 or higher)
*   Docker Compose (version 1.29.0 or higher)
*   Git

## 2. Clone the Repository

First, clone the EthosMCP repository to your local machine:

```bash
git clone https://github.com/nyayoshbharuchanb15-max/EthosMCP.git
cd EthosMCP
```

## 3. Configure Environment Variables

Create a `.env` file in the root of the project directory. This file will contain sensitive configuration details for your deployment.

```dotenv
# .env

PORT=8000
DATABASE_URL="postgresql://user:password@db:5432/ethosmcp_db"
CRYPTO_KEY="your_strong_cryptographic_key_here"
# Add other environment variables as needed
```

**Important:** Replace `your_strong_cryptographic_key_here` with a strong, randomly generated key. Do not commit this file to version control.

## 4. Build and Run with Docker Compose

Navigate to the project root directory where `docker-compose.yml` is located, and run the following command to build the Docker images and start the services:

```bash
docker-compose up --build -d
```

*   `--build`: Builds the Docker images before starting the containers.
*   `-d`: Runs the containers in detached mode (in the background).

## 5. Verify Deployment

Once the containers are running, you can verify the deployment:

*   **Check container status:**
    ```bash
    docker-compose ps
    ```
    You should see `ethosmcp-server` and `db` containers in a `Up` state.

*   **Access the MCP server:**
    The MCP server will be accessible on `http://localhost:8000` (or the port you specified in `.env`). You can interact with it using an MCP client.

## 6. Stopping and Removing Services

To stop the running services:

```bash
docker-compose stop
```

To stop and remove the containers, networks, and volumes:

```bash
docker-compose down -v
```

*   `-v`: Removes named volumes declared in the `volumes` section of the `docker-compose.yml` file.
