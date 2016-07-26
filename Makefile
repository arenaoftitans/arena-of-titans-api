FLAKE8_CMD ?= python3-flake8
JINJA2_CLI ?= jinja2
PEP8_CMD ?= python3-pep8
PYTHON_CMD ?= python3

THIS_FILE := $(lastword $(MAKEFILE_LIST))


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo "- doc: create the doc"
	@echo "- config: build config file for nginx"
	@echo "- debug: launch API in debug mode"
	@echo "- redis: start the redis database"
	@echo "- nginx: start the nginx webserver"
	@echo "- check: launch lint and testall"
	@echo "- lint: launch pep8 and pyflakes"
	@echo "- testall: launch all tests with corverage report (equivalent to `make test && make testintegration`)"
	@echo "- test: launch unit tests with coverage report"
	@echo "- testintegration: launch integration tests with coverage report"
	@echo "- testdebug: launch integration tests but don't launch the API"
	@echo "- deploy: launch `cd aot-api && make updateprod` on the production server"
	@echo "- devdeploy: launch `cd devaot && make updatedev` on the production server"
	@echo "- updateprod: restart the API after updating the git repo"
	@echo "- updatedev: restart the API after updating the git repo"
	@echo "- static: generate all static files for the API like SVG boards"


.PHONY: doc
doc:
	cd doc && make html


.PHONY: config
config:
	${JINJA2_CLI} --format=toml aot-api.dist.conf config.toml > aot-api.conf


.PHONY: debug
debug: redis nginx
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" forever -w \
	    --uid debug_aot \
	    -c python3 \
	    --watchDirectory aot \
	    aot/test_main.py


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
	${FLAKE8_CMD} --max-line-length 99 --exclude "conf.py" --exclude "aot/test" aot
	${PEP8_CMD} --max-line-length 99 aot/test


.PHONY: testall
testall: test testintegration


.PHONY: test
test:
	./setup.py test


.PHONY: tdd
tdd:
	py.test-3 aot/test --cov aot --cov-report html --cov-config .coveragerc --ignore aot/test/integration --testmon


.PHONY: testintegration
testintegration: redis
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" forever start -a \
	    -c python3 \
	    --uid test_aot \
	    --killSignal=SIGINT \
	    aot/test_main.py
	# Wait for the process to start
	sleep 10
	py.test-3.4 aot/test/integration/
	forever stop test_aot --killSignal=SIGINT


.PHONY: testdebug
testdebug:
	py.test-3.4 aot/test/integration/ -sv


.PHONY: deploy
deploy:
	git push aot -f && \
	ssh aot "cd /home/aot/aot-api && make updateprod"


.PHONY: devdeploy
devdeploy:
	git push && \
	ssh aot "cd /home/aot/devapi && make updatedev"


.PHONY: updatedev
updatedev:
	git pull && \
	sudo systemctl stop devaot && \
	$(MAKE) -f $(THIS_FILE) static && \
	sudo systemctl start devaot


.PHONY: updateprod
updateprod:
	git pull && \
	sudo systemctl stop aot && \
	$(MAKE) -f $(THIS_FILE) static && \
	sudo systemctl start aot


.PHONY: static
static:
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" ${PYTHON_CMD} scripts/gen-boards.py \
	    -i aot/resources/games/ \
	    -o static/boards
