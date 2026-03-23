# Matrix Dice Bot Dockerfile
# Multi-stage build to keep the final image small

# Stage 1: Build stage
FROM python:3.14.3-slim as builder

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.14.3-slim

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Command to run the bot
CMD ["python", "bot.py"]
