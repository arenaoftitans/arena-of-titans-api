-include Makefile.in

CONTAINER_NAME ?= aot-dev-api
DK_EXEC_CMD ?= docker-compose exec ${CONTAINER_NAME}
PRECOMMIT_CMD ?= pre-commit
PYTHON_CMD ?= python3
PYTEST_CMD ?= pytest
PYTEST_WATCH_CMD ?= ptw

# Ci Related variables. Leave empty, set only for ci.
CI_TESTS_TIMEOUT ?=
CACHE_HOST ?=


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo "Relevant targets will be launched within docker."
	@echo
	@echo "Possible targets:"
	@echo "- clean: clean generated files and containers."
	@echo "- clean-pyc-tests: remove pyc files associated to tests to run pytest from Pipenv or the container easily."
	@echo "- ci: run linters and tests in ci system. Should be run only by the CI server."
	@echo "- deps: install or update dependencies in the docker container."
	@echo "- dockerbuild: build the docker image for development. You must pass the VERSION variable."
	@echo "- dockerpush: push the image. You must pass the VERSION variable."
	@echo "- dkdev: launch API for dev. Will reload the API on file change."
	@echo "- doc: create the doc."
	@echo "- check: launch lint and tests."
	@echo "- dkcheck: launch list and tests in docker."
	@echo "- lint: launch flake8 in docker."
	@echo "- tests: launch all tests with coverage report."
	@echo "- tdd: launch unit tests in watch mode. The tests impacted by a change will be rerun on code change."


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


.PHONY: clean
clean:
	docker-compose down || echo "docker-compose down failed. Maybe docker compose is not installed."
	rm -rf .htmlcov
	rm -rf .tmontmp
	rm -rf .testmondata


.PHONY: clean-pyc-tests
clean-pyc-tests:
	find tests -name \*.pyc -exec rm {} \;


.PHONY: deps
deps:
	pip install -U pip
	pip install pipenv
	pipenv install --dev --deploy --system


.PHONY: doc
doc:
	cd doc && make html


.PHONY: dkdev
dkdev:
	docker-compose up


.PHONY: check
check: lint tests


.PHONY: dkcheck
dkcheck: clean-pyc-tests
	${DK_EXEC_CMD} make CI_TESTS_TIMEOUT=${CI_TESTS_TIMEOUT} CACHE_HOST=${CACHE_HOST} lint
	${DK_EXEC_CMD} make CI_TESTS_TIMEOUT=${CI_TESTS_TIMEOUT} CACHE_HOST=${CACHE_HOST} tests


.PHONY: lint
lint:
	${PRECOMMIT_CMD} run --all


.PHONY: tests
tests: clean-pyc-tests
	CI_TESTS_TIMEOUT=${CI_TESTS_TIMEOUT} CACHE_HOST=${CACHE_HOST} pytest --cov aot --cov-report html --cov-report term:skip-covered


.PHONY: tdd
tdd:
	"${PYTEST_WATCH_CMD}" aot tests --runner "${PYTEST_CMD}" -- tests --testmon -m 'not integration'
