#!/bin/bash

set -e

echo "Running container security checks..."

echo "Building container..."
docker build -t suggestion-box-check .

echo "Starting container..."
docker run -d --name security-check suggestion-box-check

echo "Waiting for health check..."
sleep 15

echo "Checking user..."
USER_ID=$(docker exec security-check id -u)
if [ "$USER_ID" -eq 0 ]; then
    echo "FAIL: Container running as root"
    exit 1
else
    echo "PASS: Running as user ID $USER_ID"
fi

HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' security-check)
if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "FAIL: Health status is $HEALTH_STATUS"
    exit 1
else
    echo "PASS: Health status is $HEALTH_STATUS"
fi

PORTS=$(docker port security-check)
if echo "$PORTS" | grep -q "8000"; then
    echo "PASS: Port 8000 exposed correctly"
else
    echo "FAIL: Port 8000 not exposed"
    exit 1
fi

echo "Testing API..."
sleep 5
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || true)

if [ "$RESPONSE" -eq 200 ]; then
    echo "PASS: API responding correctly"
else
    echo "FAIL: API returned HTTP $RESPONSE"
    exit 1
fi

echo "Cleaning up..."
docker stop security-check
docker rm security-check

echo "All security checks passed!"
