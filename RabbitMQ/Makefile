.PHONY: help setup deploy-infra deploy-app logs restart clean run-producer status stop

# Colors
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

help:
	@echo "${YELLOW}RabbitMQ Deployment Helper${NC}"
	@echo ""
	@echo "${GREEN}Available commands:${NC}"
	@echo "  make setup         - Create necessary directories and initial setup"
	@echo "  make deploy-infra  - Deploy RabbitMQ and monitoring infrastructure"
	@echo "  make deploy-app    - Deploy the Python application (consumer)"
	@echo "  make logs          - Show logs from the RabbitMQ container"
	@echo "  make run-producer  - Run the producer once to generate messages"
	@echo "  make restart       - Restart all containers"
	@echo "  make status        - Show status of all containers"
	@echo "  make stop          - Stop all containers"
	@echo "  make clean         - Remove all containers and volumes"

setup:
	@echo "${GREEN}Creating necessary directories...${NC}"
	mkdir -p rabbitmq prometheus grafana app
	@echo "${GREEN}Setup complete!${NC}"

deploy-infra:
	@echo "${GREEN}Deploying RabbitMQ and monitoring infrastructure...${NC}"
	docker-compose up -d rabbitmq prometheus grafana
	@echo "${GREEN}Infrastructure deployed!${NC}"
	@echo "${YELLOW}RabbitMQ Management UI: http://localhost:15672${NC}"
	@echo "${YELLOW}Prometheus: http://localhost:9090${NC}"
	@echo "${YELLOW}Grafana: http://localhost:3000${NC}"

deploy-app:
	@echo "${GREEN}Deploying Python consumer application...${NC}"
	docker-compose up -d consumer
	@echo "${GREEN}Consumer deployed!${NC}"

logs:
	@echo "${GREEN}Showing logs from RabbitMQ...${NC}"
	docker-compose logs -f rabbitmq

run-producer:
	@echo "${GREEN}Running producer to generate messages...${NC}"
	docker-compose up producer

restart:
	@echo "${GREEN}Restarting all containers...${NC}"
	docker-compose restart
	@echo "${GREEN}All containers restarted!${NC}"

status:
	@echo "${GREEN}Showing status of all containers...${NC}"
	docker-compose ps

stop:
	@echo "${GREEN}Stopping all containers...${NC}"
	docker-compose stop
	@echo "${GREEN}All containers stopped!${NC}"

clean:
	@echo "${RED}WARNING: This will remove all containers and volumes!${NC}"
	@echo "${YELLOW}Press Ctrl+C to cancel, or Enter to continue...${NC}"
	@read
	@echo "${GREEN}Removing all containers and volumes...${NC}"
	docker-compose down -v
	@echo "${GREEN}Cleanup complete!${NC}"