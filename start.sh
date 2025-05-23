#!/bin/bash

# Log startup
echo "Starting Telegram Beer Bot..."
echo "Current directory: $(pwd)"
echo "Listing directory contents:"
ls -la

# Make sure we have the token
if [ -z "$BOT_TOKEN" ]; then
  echo "ERROR: BOT_TOKEN environment variable is not set!"
  exit 1
else
  echo "BOT_TOKEN is set"
fi

# Set default port if not set
if [ -z "$PORT" ]; then
  export PORT=10000
  echo "PORT not set, defaulting to 10000"
else
  echo "Using PORT: $PORT"
fi

# Check for images
if [ ! -f "zhiguli_happy.png" ]; then
  echo "WARNING: Happy image file not found at $(pwd)/zhiguli_happy.png"
else
  echo "Found happy image at $(pwd)/zhiguli_happy.png"
fi

if [ ! -f "zhiguli_sad.png" ]; then
  echo "WARNING: Sad image file not found at $(pwd)/zhiguli_sad.png"
else
  echo "Found sad image at $(pwd)/zhiguli_sad.png"
fi

# Start the bot with debug output
echo "Starting bot..."
python main.py