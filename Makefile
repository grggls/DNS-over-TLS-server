# Makefile

#___includes___

#___vars___
BREW_DEPS=docker git
NAME=dnstlsproxy
TAG=dns2dnstlsproxy

#___config___
.DEFAULT_GOAL := test

#___targets___

# Development targets
install:  # Install dependencies with Rye
	rye sync

test: install  # Run tests
	rye run pytest

test-cov: install  # Run tests with coverage
	rye run pytest --cov=dns_over_tls_server --cov-report=html

lint: install  # Run linting
	rye run black src/ tests/
	rye run isort src/ tests/
	rye run flake8 src/ tests/

format: install  # Format code
	rye run black src/ tests/
	rye run isort src/ tests/

type-check: install  # Run type checking
	rye run mypy src/

# Legacy targets
unprepare:
	brew uninstall --force $(BREW_DEPS)

prepare:
	brew update
	brew install $(BREW_DEPS)

reprepare: unprepare prepare

rm:
	docker stop $(NAME) || true && docker rm $(NAME) || true 2> /dev/null

build:
	docker build --tag $(TAG) .

build.curl:
	docker build --build-arg STUB=curl --tag $(TAG) .

build.kdig:
	docker build --build-arg STUB=kdig --tag $(TAG) .

build.ssock:
	docker build --build-arg STUB=ssock --tag $(TAG) .

script: install
	rye run dns-over-tls-server --port 8053 --connections 3

run: build rm
	docker run --name dnstlsproxy -p 8053:8053/tcp $(TAG)

run.curl: build.curl rm
	docker run --name dnstlsproxy -p 8053:8053/tcp $(TAG)

run.kdig: build.kdig rm
	docker run --name dnstlsproxy -p 8053:8053/tcp $(TAG)

run.ssock: build.ssock rm
	docker run --name dnstlsproxy -p 8053:8053/tcp $(TAG)

interactive: build rm
	docker run -it $(TAG):latest /bin/sh

up: run.ssock
