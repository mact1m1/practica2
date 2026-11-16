PYTHON ?= python3

.PHONY: test check demo demo-real
test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

check:
	$(PYTHON) -m compileall -q src tests

demo:
	sh run.sh examples/test.toml config
	sh run.sh examples/test.toml direct
	sh run.sh examples/test.toml graph
	sh run.sh examples/cycle.toml graph
	sh run.sh examples/filtered.toml graph
	sh run.sh examples/test.toml reverse --target D
	sh run.sh examples/test.toml reverse --target Z
	sh run.sh examples/cycle.toml reverse --target A

demo-real:
	sh run.sh examples/itoa.toml graph
	sh run.sh examples/crc32fast.toml graph
	sh run.sh examples/miniz_oxide.toml graph
