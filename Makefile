PYTHON ?= python3

.PHONY: test check demo
test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

check:
	$(PYTHON) -m compileall -q src tests

demo:
	sh run.sh examples/test.toml config
