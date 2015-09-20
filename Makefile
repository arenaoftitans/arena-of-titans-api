FLAKE8_CMD ?= python3-flake8
JINJA2_CLI ?= jinja2
PEP8_CMD ?= python3-pep8
PYTHON_CMD ?= python3


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo "- check: launch lint and testall"
	@echo "- config: build config file for nginx"
	@echo "- debug: launch API in debug mode"
	@echo "- doc: create the doc"
	@echo "- lint: launch pep8 and pyflakes"
	@echo "- static: generate all static files for the API like SVG boards"
	@echo "- test: launch unit tests with coverage report"
	@echo "- testall: launch all tests with corverage report"
	@echo "- testdebug: launch integration tests but don't launch the API"
	@echo "- testintegration: launch integration tests with coverage report"


.PHONY: test
test:
	./setup.py test


.PHONY: testintegration
testintegration: redis start
	PYTHONPATH="${PYTHONPATH}:$(pwd)" forever start -a -c python3 --uid test_aot --killSignal=SIGINT aot/test_main.py
	# Wait for the process to start
	sleep 10
	py.test-3.4 aot/test/integration/
	forever stop test_aot --killSignal=SIGINT


.PHONY: start
start: static
	PYTHONPATH="${PYTHONPATH}:$(pwd)" forever start -a -c python3 --uid test_aot --killSignal=SIGINT aot/test_main.py


.PHONY: testall
testall: test testintegration


.PHONY: lint
lint:
	${FLAKE8_CMD} --max-line-length 99 --exclude "conf.py" --exclude "aot/test" aot
	${PEP8_CMD} --max-line-length 99 aot/test


.PHONY: check
check: testall lint


.PHONY: config
config:
	${JINJA2_CLI} --format=toml aot-api.dist.conf config.toml > aot-api.conf


.PHONY: debug
debug:
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" forever -w -c python3 --watchDirectory aot aot/test_main.py


.PHONY: doc
doc:
	cd doc && make html


.PHONY: testdebug
testdebug:
	py.test-3.4 aot/test/integration/ -sv


redis:
	sudo systemctl start redis


.PHONY: static
static:
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" ${PYTHON_CMD} scripts/gen-boards.py -i aot/resources/games/ -o static/boards
