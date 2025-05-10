# Reddit Service

A Telegram bot service for processing Reddit content.

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone this repository
2. Configure `config.py` with your Telegram bot token and other settings
3. Start the service with Docker Compose:

```bash
# Using start.sh script
chmod +x start.sh
./start.sh

# Or directly with Docker Compose
docker-compose up -d
```

## Management Commands

```bash
# View logs
docker-compose logs -f

# View logs with timestamps
docker-compose logs -f --timestamps

# View only the last 100 lines of logs
docker-compose logs -f --tail=100

# Filter logs for Docker-specific messages
docker-compose logs -f | grep "\[DOCKER\]"

# Stop the service
docker-compose down

# Restart the service
docker-compose restart
```

## Log Files

The service maintains two log files that are mounted as volumes:

- `logs_errors.txt`: Contains detailed error logs
- `logs_fails.txt`: Contains logs for failed content extraction attempts

Docker Compose logs are configured with a 10MB size limit and 3 rotated files.
