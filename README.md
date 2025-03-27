# Notifications Service

## Description

Service for managing notifications. Service provides REST API, WebSocket API, web page, monitoring tools.

## Features

- Create notification: Create new notification.
- Get notification: Show notification by unique uuid.
- Get many notifications: Fetch notification using pagination.
- Read notification: You can make notification read.
- Stream recent notifications: Real-time loading of recent notifications.
- Notification analysis: Separated analyze service.
- Get notification processing status: You can watch current status of notification's analysis.
- Simple interface: You can try to interact with API interactively.

## Getting Started

### Prerequisites

Ensure you have Docker and Docker Compose installed on your machine.

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repository.git
   cd your-repository
2. Create .env and .env_test (if necessary) and paste the following:
```editorconfig
LOGGING_FORMAT="[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-3d %(levelname)-7s - %(message)s"
LOGGING_LEVEL="INFO"

DB_USER="backend_user"
DB_NAME="postgres"
DB_PASSWORD=1234
DB_HOST="database"
DB_PORT=5432

REDIS_HOST="redis"
REDIS_PORT=6379

APP_HOST="0.0.0.0"
APP_PORT=8000
```
3. Start an application:
```bash
docker-compose up -d --build
```

## How to use

If you used my .env, so you can use the following urls:

- API docs for REST API: http://localhost:8000/api/docs
- WebSockets API: ws://localhost:8000/api/notification/stream
- Prometheus: http://localhost:9090/
- Grafana (standart credentials admin:admin): http://localhost:3000/
- Web interface: http://localhost:8000/