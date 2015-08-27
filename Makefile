.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo "- test: launch unit tests with coverage report"
	@echo "- testintegration: launch integration tests with coverage report"
	@echo "- testall: launch all tests with corverage report"
	@echo "- lint: launch pep8 and pyflakes"
	@echo "- check: launch lint and testall"
	@echo "- debug: launch API in debug mode"
	@echo "- testdebug: launch integration tests but don't launch the API"


.PHONY:
test:
	./setup.py test


.PHONY:
testintegration: redis
	PYTHONPATH=$PYTHONPATH:$(pwd) forever start -w -c python3 --uid test_aot --watchDirectory aot aot/test_main.py --watchIgnore aot/test --watchIgnore \*.pyc
	# Wait for the process to start
	sleep 10
	py.test-3.4 aot/test/integration/test_api.py
	forever stop test_aot

.PHONY:
testall: test testintegration


.PHONY:
pep8:
	pep8 --max-line-length 99 aot


.PHONY:
pyflakes:
	python3-pyflakes aot


.PHONY:
lint: pep8 pyflakes


.PHONY:
check: testall lint


.PHONY:
debug:
	PYTHONPATH=$PYTHONPATH:$(pwd) forever -w -c python3 --watchDirectory aot aot/test_main.py --watchIgnore aot/test --watchIgnore \*.pyc


.PHONY:
testdebug:
	py.test-3.4 aot/test/integration/test_api.py


redis:
	sudo systemctl start redis
