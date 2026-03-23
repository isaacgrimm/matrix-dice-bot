# Matrix Dice Bot - Docker Deployment

This guide explains how to deploy the Matrix Dice Bot using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)
- Matrix account credentials

## Quick Start

### 1. Build the Docker Image

```bash
cd matrix-dice-bot
docker build -t matrix-dice-bot .
```

### 2. Run the Bot

```bash
docker run -d \
  -e MATRIX_HOMESERVER=https://matrix.org \
  -e MATRIX_USERNAME=@yourbot:matrix.org \
  -e MATRIX_PASSWORD=your_password \
  -e MATRIX_ROOM=!roomid:matrix.org \
  --name dice-bot \
  matrix-dice-bot
```

### 3. Using Access Token (Recommended)

```bash
docker run -d \
  -e MATRIX_HOMESERVER=https://matrix.org \
  -e MATRIX_USERNAME=@yourbot:matrix.org \
  -e MATRIX_ACCESS_TOKEN=your_access_token \
  -e MATRIX_ROOM=!roomid:matrix.org \
  --name dice-bot \
  matrix-dice-bot
```

## Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  dice-bot:
    build: .
    environment:
      - MATRIX_HOMESERVER=https://matrix.org
      - MATRIX_USERNAME=@yourbot:matrix.org
      - MATRIX_ACCESS_TOKEN=your_access_token
      - MATRIX_ROOM=!roomid:matrix.org
      - LOG_LEVEL=INFO
    restart: unless-stopped
    volumes:
      - ./bot.log:/app/bot.log
```

Then run:

```bash
docker-compose up -d
```

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `MATRIX_HOMESERVER` | Yes | Matrix homeserver URL | `https://matrix.org` |
| `MATRIX_USERNAME` | Yes | Bot username (e.g., `@yourbot:matrix.org`) | - |
| `MATRIX_PASSWORD` | No | Bot password (use either password or access token) | - |
| `MATRIX_ACCESS_TOKEN` | No | Access token (recommended over password) | - |
| `MATRIX_ROOM` | Yes | Room ID or alias to join | - |
| `LOG_LEVEL` | No | Logging level (DEBUG, INFO, ERROR) | `INFO` |

## Persisting Logs

To persist logs outside the container:

```bash
docker run -d \
  -e MATRIX_HOMESERVER=https://matrix.org \
  -e MATRIX_USERNAME=@yourbot:matrix.org \
  -e MATRIX_ACCESS_TOKEN=your_access_token \
  -e MATRIX_ROOM=!roomid:matrix.org \
  -v $(pwd)/bot.log:/app/bot.log \
  --name dice-bot \
  matrix-dice-bot
```

## Viewing Logs

```bash
# View real-time logs
docker logs -f dice-bot

# View historical logs
docker logs dice-bot
```

## Stopping the Bot

```bash
docker stop dice-bot
```

## Restarting the Bot

```bash
docker start dice-bot
```

## Rebuilding the Image

If you update the bot code:

```bash
docker build -t matrix-dice-bot .
docker stop dice-bot
docker rm dice-bot
docker run -d ... (same command as before)
```

## Using with Docker Compose

For easier management, use Docker Compose:

```bash
# Start the bot
docker-compose up -d

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart dice-bot

# View logs
docker-compose logs -f
```

## Troubleshooting

### Bot doesn't respond to commands

1. Check logs: `docker logs dice-bot`
2. Verify the bot joined the correct room
3. Ensure the bot has permissions to send messages

### Authentication errors

1. Verify credentials in environment variables
2. Try using an access token instead of password
3. Check if the account is locked or suspended

### Connection issues

1. Verify the homeserver URL is correct
2. Check your internet connection
3. Ensure the Matrix server is accessible

## Advanced Configuration

### Custom Python Version

To use a different Python version, change the base image in the Dockerfile:

```dockerfile
FROM python:3.10-slim as builder
```

### Adding Additional Dependencies

Add them to `requirements.txt` and rebuild the image.

### Custom Entry Point

Override the entry point for custom behavior:

```bash
docker run -d ... --entrypoint /custom/entrypoint.sh matrix-dice-bot
```

## Security Best Practices

1. **Never commit `.env` files** - Use environment variables
2. **Use access tokens** - More secure than passwords
3. **Restrict permissions** - Limit bot permissions in Matrix
4. **Keep updated** - Regularly rebuild with the latest code
5. **Use volumes for logs** - Persist logs securely

## Example with All Options

```bash
docker run -d \
  -e MATRIX_HOMESERVER=https://matrix.org \
  -e MATRIX_USERNAME=@yourbot:matrix.org \
  -e MATRIX_ACCESS_TOKEN=your_access_token_here \
  -e MATRIX_ROOM=!roomid:matrix.org \
  -e LOG_LEVEL=DEBUG \
  -v $(pwd)/bot.log:/app/bot.log \
  --restart unless-stopped \
  --name dice-bot \
  matrix-dice-bot
```

This configuration:
- Uses access token authentication
- Sets debug logging
- Persists logs to the host
- Automatically restarts unless explicitly stopped
- Names the container for easy management