-include Makefile.in

FLAKE8_CMD ?= /usr/bin/python3-flake8
JINJA2_CLI ?= /usr/bin/jinja2
PYTHON_CMD ?= /usr/bin/python3
PYTEST_CMD ?= /usr/bin/py.test-3
PYTEST_WATCH_CMD ?= /usr/bin/ptw-3

THIS_FILE := $(lastword $(MAKEFILE_LIST))

type ?= dev
version ?= latest


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo "- doc: create the doc"
	@echo "- dev: launch API for dev. Will reload the API on file change."
	@echo "- redis: start the redis database"
	@echo "- nginx: start the nginx webserver"
	@echo "- check: launch lint and testall"
	@echo "- lint: launch flake8"
	@echo "- testall: launch all tests with corverage report (equivalent to make test && make testintegration)"
	@echo "- test: launch unit tests with coverage report"
	@echo "- testintegration: launch integration tests with coverage report. The API must be running on dev mode."
	@echo "- static: generate all static files for the API like SVG boards"


.PHONY: doc
doc:
	cd doc && make html


.PHONY: dev
dev: redis nginx
	rm -f *.sock
	PYTHONPATH="${PYTHONPATH}:$(pwd)" python3 aot/test_main.py


.PHONY: redis
redis:
	sudo systemctl start redis


.PHONY: nginx
nginx:
	sudo systemctl start nginx


.PHONY: check
check: lint testall


.PHONY: lint
lint:
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
	./setup.py test


.PHONY: tdd
tdd:
	"${PYTEST_WATCH_CMD}" aot --runner "${PYTEST_CMD}" -- aot/test --ignore aot/test/integration --ignore aot/test_main.py --testmon


.PHONY: testintegration
testintegration:
	"${PYTEST_CMD}" aot/test/integration/


.PHONY: static
static:
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" ${PYTHON_CMD} scripts/gen-boards.py \
	    -i aot/resources/games/ \
	    -o static/boards
