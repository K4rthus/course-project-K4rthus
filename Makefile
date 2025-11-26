.PHONY: build run test scan security-check clean

# Build the container
build:
	docker compose build

# Run the application
run:
	docker compose up -d

# Stop the application
stop:
	docker compose down

# Run security checks
security-check:
	chmod +x scripts/check-container.sh
	./scripts/check-container.sh

# Security scanning
scan:
	docker compose build
	hadolint Dockerfile
	trivy image suggestion-box-app:latest

# Clean up
clean:
	docker compose down -v
	docker system prune -f

# View logs
logs:
	docker compose logs -f suggestion-box

# Health check
health:
	curl -f http://localhost:8000/health

# Show container info
info:
	@echo "=== Container Information ==="
	docker images suggestion-box-app --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
	@echo ""
	@echo "=== Running Containers ==="
	docker ps --filter "name=suggestion-box" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
