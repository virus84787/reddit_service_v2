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

# Stop the service
docker-compose down

# Restart the service
docker-compose restart
```
