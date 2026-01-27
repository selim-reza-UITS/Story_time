# Cyndi Story Telling - Makefile
# ================================

# Variables
DOCKER_COMPOSE = docker compose
BACKEND_CONTAINER = cyndi_backend
AI_CONTAINER = cyndi_ai_helper
DB_CONTAINER = cyndi_db

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

# ===================
# 🚀 Quick Start
# ===================

.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)Cyndi Story Telling - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

.PHONY: up
up: ## Start all services
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ All services started$(NC)"
	@echo "  Backend:    http://localhost:9900"
	@echo "  AI Helper:  http://localhost:9901"
	@echo "  PostgreSQL: localhost:5435"
	@echo "  Redis:      localhost:6377"

.PHONY: down
down: ## Stop all services
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ All services stopped$(NC)"

.PHONY: restart
restart: down up ## Restart all services

# ===================
# 📦 Build
# ===================

.PHONY: build
build: ## Build all Docker images
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ All images built$(NC)"

.PHONY: build-backend
build-backend: ## Build backend image only
	$(DOCKER_COMPOSE) build backend
	@echo "$(GREEN)✓ Backend image built$(NC)"

.PHONY: build-ai
build-ai: ## Build AI helper image only
	$(DOCKER_COMPOSE) build ai-helper
	@echo "$(GREEN)✓ AI helper image built$(NC)"

.PHONY: rebuild
rebuild: ## Force rebuild all images (no cache)
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ All images rebuilt$(NC)"

# ===================
# 🗄️ Database
# ===================

.PHONY: migrate
migrate: ## Run Django migrations
	$(DOCKER_COMPOSE) exec backend python manage.py migrate
	@echo "$(GREEN)✓ Migrations applied$(NC)"

.PHONY: makemigrations
makemigrations: ## Create new migrations
	$(DOCKER_COMPOSE) exec backend python manage.py makemigrations
	@echo "$(GREEN)✓ Migrations created$(NC)"

.PHONY: createsuperuser
createsuperuser: ## Create Django superuser
	$(DOCKER_COMPOSE) exec backend python manage.py createsuperuser

.PHONY: shell
shell: ## Open Django shell
	$(DOCKER_COMPOSE) exec backend python manage.py shell

.PHONY: dbshell
dbshell: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec db psql -U cyndi_user -d cyndi_db

# ===================
# 📋 Logs
# ===================

.PHONY: logs
logs: ## View all logs
	$(DOCKER_COMPOSE) logs -f

.PHONY: logs-backend
logs-backend: ## View backend logs
	$(DOCKER_COMPOSE) logs -f backend

.PHONY: logs-ai
logs-ai: ## View AI helper logs
	$(DOCKER_COMPOSE) logs -f ai-helper

.PHONY: logs-db
logs-db: ## View database logs
	$(DOCKER_COMPOSE) logs -f db

# ===================
# 🐚 Shell Access
# ===================

.PHONY: bash-backend
bash-backend: ## Open bash in backend container
	$(DOCKER_COMPOSE) exec backend bash

.PHONY: bash-ai
bash-ai: ## Open bash in AI helper container
	$(DOCKER_COMPOSE) exec ai-helper bash

# ===================
# 🧹 Cleanup
# ===================

.PHONY: clean
clean: ## Remove containers and networks
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo "$(GREEN)✓ Cleaned up containers and volumes$(NC)"

.PHONY: clean-images
clean-images: ## Remove unused Docker images
	docker image prune -f
	@echo "$(GREEN)✓ Cleaned up unused images$(NC)"

.PHONY: clean-all
clean-all: clean clean-images ## Full cleanup (containers + images)
	@echo "$(GREEN)✓ Full cleanup completed$(NC)"

# ===================
# 📊 Status
# ===================

.PHONY: ps
ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

.PHONY: status
status: ## Show detailed service status
	@echo "$(GREEN)=== Container Status ===$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(GREEN)=== Port Mappings ===$(NC)"
	@echo "  Backend:    http://localhost:9900 → container:8000"
	@echo "  AI Helper:  http://localhost:9901 → container:8000"
	@echo "  PostgreSQL: localhost:5435 → container:5432"
	@echo "  Redis:      localhost:6377 → container:6379"

# ===================
# 🧪 Development
# ===================

.PHONY: dev
dev: ## Start services in development mode with logs
	$(DOCKER_COMPOSE) up

.PHONY: test
test: ## Run backend tests
	$(DOCKER_COMPOSE) exec backend python manage.py test

.PHONY: collectstatic
collectstatic: ## Collect static files
	$(DOCKER_COMPOSE) exec backend python manage.py collectstatic --noinput

# ===================
# 🔧 Utilities
# ===================

.PHONY: pip-install
pip-install: ## Install new pip package (usage: make pip-install pkg=package_name)
	$(DOCKER_COMPOSE) exec backend pip install $(pkg)
	$(DOCKER_COMPOSE) exec backend pip freeze > Backend/requirements.txt
	@echo "$(GREEN)✓ Package $(pkg) installed and requirements.txt updated$(NC)"

.PHONY: api-docs
api-docs: ## Show API documentation
	@cat API_ENDPOINTS.md
