.PHONY: bootstrap dev backend frontend test

# Bootstrap the project, installing all dependencies
bootstrap:
	@echo "Installing Python dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Installing Node.js dependencies..."
	cd web-frontend && npm install
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "Setup complete! 🎉"

# Run the entire development stack
dev:
	@echo "Starting backend and frontend development servers..."
	$(MAKE) backend & $(MAKE) frontend

# Run only the backend
backend:
	@echo "Starting backend server..."
	cd backend && python main.py

# Run only the frontend
frontend:
	@echo "Starting frontend development server..."
	cd web-frontend && npm run dev

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && pytest -q
	@echo "Running frontend tests..."
	cd web-frontend && npm test

# Run E2E tests
test-e2e:
	@echo "Running E2E tests..."
	cd web-frontend && npm run test:e2e

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	rm -rf web-frontend/dist
	rm -rf web-frontend/node_modules
	@echo "Cleanup complete! 🧹"

# Show help information
help:
	@echo "Emotion Agent Hackathon Project"
	@echo ""
	@echo "make bootstrap  : Install all dependencies"
	@echo "make dev        : Run backend and frontend dev servers"
	@echo "make backend    : Run only the backend server"
	@echo "make frontend   : Run only the frontend dev server"
	@echo "make test       : Run all tests"
	@echo "make test-e2e   : Run end-to-end tests"
	@echo "make clean      : Remove generated files" 