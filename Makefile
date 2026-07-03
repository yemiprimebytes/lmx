# Python and Django setup
PYTHON = python
MANAGE = $(PYTHON) manage.py

# Run Django server
runserver:
	$(MANAGE) runserver localhost:6600

# Database migrations
migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

# Celery workers
celery-worker:
	celery -A project worker -l info

celery-beat:
	celery -A project beat -l info

# Redis
redis-start:
	redis-server

# Testing & linting
test:
	$(MANAGE) test

lint:
	flake8 .

format:
	black .

# Clean up junk files
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

# Help menu for teammates
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
 | sort \
 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
