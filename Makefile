-include Makefile.in

INSIDE_DOCKER := $(shell grep -q docker /proc/self/cgroup && echo true)
CONTAINER_NAME ?= aot-dev-api

DK_EXEC_CMD ?= docker-compose exec ${CONTAINER_NAME}
FLAKE8_CMD ?= flake8
VENV_FLAKE8_CMD ?= ~/.virtualenvs/aot/bin/flake8
PYTHON_CMD ?= python3
PYTEST_CMD ?= pytest
PYTEST_WATCH_CMD ?= ptw

type ?= dev
version ?= latest


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo "Relevant targets will be launched within docker."
	@echo
	@echo "Possible targets:"
	@echo "- clean: clean generated files and containers."
	@echo "- ci: run linters and tests in ci system. Should be run only in bitbucket pipelines."
	@echo "- cicfg: build config for bitbucket pipelines."
	@echo "- deps: install or update dependencies in the docker container."
	@echo "- rundeps: install or update dependencies."
	@echo "- dev: launch API for dev. Will reload the API on file change."
	@echo "- doc: create the doc."
	@echo "- check: launch lint and testall."
	@echo "- lint: launch flake8 in docker."
	@echo "- venvlint: launch flake8 with command defined by VENV_FLAKE8_CMD on host."
	@echo "- runlint: launch flake8."
	@echo "- testall: launch all tests with corverage report (equivalent to make test && make testintegration)."
	@echo "- test: launch unit tests with coverage report."
	@echo "- testintegration: launch integration tests with coverage report. The API must be running on dev mode."
	@echo "- static: generate all static files for the API like SVG boards."


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
	make rundeps
else
	${DK_EXEC_CMD} make deps
endif


.PHONY: rundeps
rundeps:
	pip install -U pip
	pip install -r requires.txt
	pip install -r tests_requires.txt


.PHONY: doc
doc:
	cd doc && make html


.PHONY: dev
dev:
ifdef INSIDE_DOCKER
	python3 -m aot --reload
else
	docker-compose up
endif


.PHONY: check
check: lint testall


.PHONY: ci
ci: deps cicfg lint test


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
	${FLAKE8_CMD} --max-line-length 99 \
	   --exclude "conf.py" \
	   --exclude "aot/test" \
	   --inline-quotes "'" \
	   --multiline-quotes "'''" \
	   --ignore none \
	   aot
	${FLAKE8_CMD} --max-line-length 99 \
	    --inline-quotes "'" \
	    --multiline-quotes "'''" \
	    --ignore=F811,F401 \
	    aot/test/


.PHONY: testall
testall: test testintegration


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
	"${PYTEST_WATCH_CMD}" aot --runner "${PYTEST_CMD}" -- aot/test --ignore aot/test/integration --ignore aot/test_main.py --testmon
else
	${DK_EXEC_CMD} make tdd
endif


.PHONY: testintegration
testintegration:
ifdef INSIDE_DOCKER
	"${PYTEST_CMD}" aot/test/integration/
else
	${DK_EXEC_CMD} make testintegration
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
