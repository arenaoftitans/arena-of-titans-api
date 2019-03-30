-include Makefile.in

INSIDE_DOCKER := $(shell grep -q docker /proc/self/cgroup && echo true)
CONTAINER_NAME ?= aot-dev-api

DK_EXEC_CMD ?= docker-compose exec ${CONTAINER_NAME}
FLAKE8_CMD ?= flake8
PYTHON_CMD ?= python3
PYTEST_CMD ?= pytest
PYTEST_WATCH_CMD ?= ptw

# Ci Related variables. Leave empty, set only for ci.
CI_TESTS_TIMEOUT ?=

# venv related commands
VENV_FLAKE8_CMD ?=


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo "Relevant targets will be launched within docker."
	@echo
	@echo "Possible targets:"
	@echo "- clean: clean generated files and containers."
	@echo "- ci: run linters and tests in ci system. Should be run only by the CI server."
	@echo "- deps: install or update dependencies in the docker container."
	@echo "- dockerbuild: build the docker image for development. You must pass the VERSION variable."
	@echo "- dockerpush: push the image. You must pass the VERSION variable."
	@echo "- dockerimage: build a production like image with the API installed in it."
	@echo "- dev: launch API for dev. Will reload the API on file change."
	@echo "- doc: create the doc."
	@echo "- check: launch lint and testall."
	@echo "- lint: launch flake8 in docker."
	@echo "- venvlint: launch flake8 with command defined by VENV_FLAKE8_CMD on host."
	@echo "- runlint: launch flake8."
	@echo "- test: launch unit tests with coverage report."
	@echo "- static: generate all static files for the API like SVG boards."


.PHONY: dockerbuild
dockerbuild:
ifdef VERSION
	# Update base.
	docker build \
		--pull \
		-f docker/aot-api-base/Dockerfile \
		-t "registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:${VERSION}" \
	    -t "registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:latest" \
	    .
	# Update dev image.
	docker build \
	    -f docker/aot-api-dev/Dockerfile \
	    -t "registry.gitlab.com/arenaoftitans/arena-of-titans-api/dev/aot-api:${VERSION}" \
	    -t "registry.gitlab.com/arenaoftitans/arena-of-titans-api/dev/aot-api:latest" \
	    .
	@echo "If this image works, don't forget to:"
	@echo "  - Change the version of the image in ``docker-compose.yml``"
	@echo "  - Push the image to docker: ``make VERSION=VER dockerpush"
else
	@echo "You must supply VERSION"
	exit 1
endif


.PHONY: dockerpush
dockerpush:
ifdef VERSION
	# Push base image.
	docker push "registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:${VERSION}"
	docker push "registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:latest"
	# Push dev image.
	docker push "registry.gitlab.com/arenaoftitans/arena-of-titans-api/dev/aot-api:${VERSION}"
	docker push "registry.gitlab.com/arenaoftitans/arena-of-titans-api/dev/aot-api:latest"
else
	@echo "You must supply VERSION"
	exit 1
endif


.PHONY: dockerimage
dockerimage:
ifdef VERSION
	docker build \
		--pull \
	    -f docker/aot-api/Dockerfile \
	    -t "registry.gitlab.com/arenaoftitans/arena-of-titans-api:${VERSION}" \
	    .
	# Testing image
	docker run \
		-d \
		--rm \
		--name aot-api-test \
		-e ENV=development \
		"registry.gitlab.com/arenaoftitans/arena-of-titans-api:${VERSION}"
	sleep 10
	@if [ "$$(docker inspect aot-api-test -f '{{ .State.Status }}')" = 'running' ]; then \
		echo '***** Working *****'; \
	else \
		echo '***** Failed! *****'; \
		exit 1; \
	fi
	docker stop aot-api-test
else
	@echo "You must supply VERSION"
	exit 1
endif


.PHONY: clean
clean:
	docker-compose down
	rm -rf dist
	rm -rf static
	rm -rf .htmlcov
	rm -rf .htmlcovapi
	rm -rf Arena_of_Titans_API.egg-info
	rm -rf .eggs
	rm -rf .tmontmp
	rm -rf .testmondata


.PHONY: deps
deps:
ifdef INSIDE_DOCKER
	pip install -U pip
	pip install pipenv
	pipenv install --dev --deploy --system
else
	${DK_EXEC_CMD} make deps
endif


.PHONY: doc
doc:
	cd doc && make html


.PHONY: dev
dev:
ifdef INSIDE_DOCKER
	@echo "Cannot be launched within docker, see command in docker compose to see what to do."
	exit 1
else
	docker-compose up
endif


.PHONY: check
check: lint testall


.PHONY: ci
ci: test


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
	CI_TESTS_TIMEOUT=${CI_TESTS_TIMEOUT} pytest --cov aot --cov-report html --cov-report term:skip-covered
else
	# Clean old pyc files for pytest to prevent errors if tests where run outside the container.
	find aot/test -name \*.pyc -exec rm {} \;
	${DK_EXEC_CMD} make CI_TESTS_TIMEOUT=${CI_TESTS_TIMEOUT} test
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
