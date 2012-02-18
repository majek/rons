.PHONY: all
all: deps

.PHONY: deps
deps: venv/.ok

venv:
	virtualenv venv

venv/.ok: requirements.txt venv
	./venv/bin/pip install -r requirements.txt
	touch venv/.ok

distclean::
	rm -rf venv
