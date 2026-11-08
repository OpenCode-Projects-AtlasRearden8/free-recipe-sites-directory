# Free Recipe Sites Directory — developer commands
PY := python3

.PHONY: build check verify all clean

build:
	$(PY) build.py

check: build
	$(PY) linkcheck.py

internal-only:
	$(PY) build.py && $(PY) linkcheck.py --internal

all: build check
	@echo "Verify pass: built pages exist and link check reported no failures."

verify: all

clean:
	rm -rf dist
