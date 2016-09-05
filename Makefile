FLAKE8_CMD ?= /usr/bin/python3-flake8
JINJA2_CLI ?= /usr/bin/jinja2
PEP8_CMD ?= /usr/bin/python3-pep8
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
	@echo "- config: build config file for nginx"
	@echo "- dev: launch API for dev. Will reload the API on file change."
	@echo "- redis: start the redis database"
	@echo "- nginx: start the nginx webserver"
	@echo "- check: launch lint and testall"
	@echo "- lint: launch pep8 and pyflakes"
	@echo "- testall: launch all tests with corverage report (equivalent to make test && make testintegration)"
	@echo "- test: launch unit tests with coverage report"
	@echo "- testintegration: launch integration tests with coverage report. The API must be running on dev mode."
	@echo "- static: generate all static files for the API like SVG boards"
	@echo "- deployprod: deploy front and API to the production server"
	@echo "- deploystaging: deploy front and API to the staging server"
	@echo "- deploytesting: deploy front and API to the user defined staging server"
	@echo "- collectprod: remove all unused fronts and APIs from the production server"
	@echo "- collectstaging: remove all unused fronts and APIs from the staging server"
	@echo "- collecttesting: remove all unused fronts and APIs from the user defined staging server"


.PHONY: doc
doc:
	cd doc && make html


.PHONY: config
config:
	${JINJA2_CLI} --format=toml \
		-Dtype="${type}" \
		templates/aot-api.dist.conf \
		"config/config.${type}.toml" > aot-api.conf
	${JINJA2_CLI} --format=toml \
		-Dtype="${type}" \
		templates/aot.dist.conf \
		"config/config.${type}.toml" > aot.conf
	${JINJA2_CLI} --format=toml \
	    -Dcurrent_dir=$(shell pwd) \
	    -Dtype="${type}" \
	    -Dversion="${version}" \
	    templates/uwsgi.dist.ini \
	    "config/config.${type}.toml" > uwsgi.ini
	${JINJA2_CLI} --format=toml \
	    -Dtype="${type}" \
	    -Dversion="${version}" \
	    templates/redis.dist.conf \
	    "config/config.${type}.toml" > "redis.conf"


.PHONY: debuguwsgi
debuguwsgi: redis nginx uwsgi
	tail -f api.log


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


.PHONY: deployprod
deployprod:
	./scripts/cli.sh deploy prod


.PHONY: deploystaging
deploystaging:
	./scripts/cli.sh deploy staging


.PHONY: deploytesting
deploytesting:
	./scripts/cli.sh deploy testing


.PHONY: collectprod
collectprod:
	./scripts/cli.sh collect prod


.PHONY: collectstaging
collectstaging:
	./scripts/cli.sh collect staging


.PHONY: collecttesting
collecttesting:
	./scripts/cli.sh collect testing


.PHONY: static
static:
	PYTHONPATH="${PYTHONPATH}:$(shell pwd)" ${PYTHON_CMD} scripts/gen-boards.py \
	    -i aot/resources/games/ \
	    -o static/boards
