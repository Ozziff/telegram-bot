#!/bin/bash

# Log startup
echo "Starting Telegram Beer Bot..."

# Make sure we have the token
if [ -z "$BOT_TOKEN" ]; then
  echo "ERROR: BOT_TOKEN environment variable is not set!"
  exit 1
fi

# Set default port if not set
if [ -z "$PORT" ]; then
  export PORT=10000
  echo "PORT not set, defaulting to 10000"
else
  echo "Using PORT: $PORT"
fi

# Check for images
if [ ! -f "zhiguli_happy.png" ] || [ ! -f "zhiguli_sad.png" ]; then
  echo "WARNING: Image files not found. The bot may not be able to send images."
fi

# Start the bot
python main.py