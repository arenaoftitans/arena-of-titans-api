FLAKE8_CMD ?= /usr/bin/python3-flake8
JINJA2_CLI ?= /usr/bin/jinja2
PEP8_CMD ?= /usr/bin/python3-pep8
PYTHON_CMD ?= /usr/bin/python3
PYTEST_CMD ?= /usr/bin/py.test-3
PYTEST_WATCH_CMD ?= /usr/bin/ptw-3

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
	${JINJA2_CLI} --format=toml conf/aot-api.dist.conf config.toml > aot-api.conf
	${JINJA2_CLI} --format=toml -Dcurrent_dir=$(shell pwd) conf/uwsgi.dist.ini config.toml > uwsgi.ini


.PHONY: debug
debug: redis nginx uwsgi
	tail -f api.log


.PHONY: redis
redis:
	sudo systemctl start redis


.PHONY: nginx
nginx:
	sudo systemctl start nginx


.PHONY: uwsgi
uwsgi:
	echo > api.log
	chown $(shell whoami):uwsgi api.log
	sudo systemctl start uwsgi


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
	"${PYTEST_WATCH_CMD}" aot --runner "${PYTEST_CMD}" -- aot/test --ignore aot/test/integration --ignore aot/test_main.py --testmon


.PHONY: testintegration
testintegration:
	"${PYTEST_CMD}" aot/test/integration/


.PHONY: testdebug
testdebug: redis
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" forever start -a \
	    -c "${PYTHON_CMD}" \
	    --uid test_aot \
	    --killSignal=SIGINT \
	    aot/test_main.py
	# Wait for the process to start
	sleep 10
	"${PYTEST_CMD}" aot/test/integration/
	forever stop test_aot --killSignal=SIGINT


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
