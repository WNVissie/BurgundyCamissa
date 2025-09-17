#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Ensure the database is in a clean, seeded state
echo "Seeding the database for test..."
python run_seed.py

# Start the server in the background
echo "Starting server..."
python src/main.py > server.log 2>&1 &
SERVER_PID=$!

# Wait for the server to be ready
echo "Waiting for server to start..."
# Use a loop to check if the port is open
for i in {1..10}; do
    if curl -s http://127.0.0.1:5001/ping > /dev/null; then
        echo "Server is up!"
        break
    fi
    sleep 1
done

# Run the smoke test
echo "Running smoke test..."
python test_smoke.py
TEST_EXIT_CODE=$?

# Kill the server
echo "Killing server with PID $SERVER_PID..."
kill $SERVER_PID

# Wait for server to shut down
sleep 2

echo "Testing complete."

# Exit with the test's exit code
exit $TEST_EXIT_CODE
