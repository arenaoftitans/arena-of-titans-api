-include Makefile.in

INSIDE_DOCKER := $(shell grep -q docker /proc/self/cgroup && echo true)
CONTAINER_NAME ?= aot-dev-api

DK_EXEC_CMD ?= docker-compose exec ${CONTAINER_NAME}
FLAKE8_CMD ?= flake8
PIP_CMD ?= pip
PYTHON_CMD ?= python3
PYTEST_CMD ?= pytest
PYTEST_WATCH_CMD ?= ptw

type ?= dev
version ?= latest

# venv related commands
VENV_FLAKE8_CMD ?= 


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo "Relevant targets will be launched within docker."
	@echo
	@echo "Possible targets:"
	@echo "- builddocker: build the docker image for development. You must pass the VERSION variable."
	@echo "- clean: clean generated files and containers."
	@echo "- ci: run linters and tests in ci system. Should be run only by the CI server."
	@echo "- cicfg: build config for CI."
	@echo "- deps: install or update dependencies in the docker container."
	@echo "- rundeps: install or update dependencies."
	@echo "- dev: launch API for dev. Will reload the API on file change."
	@echo "- doc: create the doc."
	@echo "- check: launch lint and testall."
	@echo "- lint: launch flake8 in docker."
	@echo "- venvlint: launch flake8 with command defined by VENV_FLAKE8_CMD on host."
	@echo "- runlint: launch flake8."
	@echo "- test: launch unit tests with coverage report."
	@echo "- static: generate all static files for the API like SVG boards."


.PHONY: builddocker
builddocker:
ifdef VERSION
	docker pull docker.io/python:3.6-slim
	docker build -f docker/aot-api/Dockerfile -t "registry.gitlab.com/arenaoftitans/arena-of-titans-api:${VERSION}" .
	@echo "If this image works, don't forget to:"
	@echo "  - Change the version of the image in ``docker-compose.yml``"
	@echo "  - Push the image to docker: ``docker push registry.gitlab.com/arenaoftitans/arena-of-titans-api:${VERSION}``"
else
	@echo "You must supply VERSION"
	exit 1
endif


.PHONY: clean
clean:
	docker-compose down
	rm -rf static
	rm -rf htmlcov
	rm -rf htmlcovapi
	rm -rf Arena_of_Titans_API.egg-info
	rm -rf .eggs
	rm -rf .tmontmp
	rm -rf .testmondata


.PHONY: deps
deps:
ifdef INSIDE_DOCKER
	make PIP_CMD="${PIP_CMD}" rundeps
else
	${DK_EXEC_CMD} make deps
endif


.PHONY: rundeps
rundeps:
	${PIP_CMD} install -U pip
	${PIP_CMD} install pipenv
	pipenv install --dev --deploy --system


.PHONY: doc
doc:
	cd doc && make html


.PHONY: dev
dev:
ifdef INSIDE_DOCKER
	python3 -m aot --reload
else
	# Empty log file
	mkdir -p logs
	echo > logs/aot-api.log
	docker-compose up
endif


.PHONY: check
check: lint testall


.PHONY: ci
ci: cicfg test


.PHONY: cicfg
cicfg:
	# Use sample config file as dev config file for redis related unit tests to pass.
	cp config/config.staging.toml config/config.dev.toml


.PHONY: lint
lint:
ifdef INSIDE_DOCKER
	make runlint
else
	${DK_EXEC_CMD} make lint
endif


.PHONY: venvlint
venvlint:
	FLAKE8_CMD=${VENV_FLAKE8_CMD} make runlint


.PHONY: runlint
runlint:
	${FLAKE8_CMD}


.PHONY: testall
testall: test


.PHONY: test
test:
ifdef INSIDE_DOCKER
	./setup.py test
else
	${DK_EXEC_CMD} make test
endif


.PHONY: tdd
tdd:
ifdef INSIDE_DOCKER
	"${PYTEST_WATCH_CMD}" aot --runner "${PYTEST_CMD}" -- aot/test --testmon
else
	${DK_EXEC_CMD} make tdd
endif


.PHONY: static
static:
ifdef INSIDE_DOCKER
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" ${PYTHON_CMD} scripts/gen-boards.py \
	    -i aot/resources/games/ \
	    -o static/boards
else
	${DK_EXEC_CMD} make static
endif
