.SUFFIXES:

SHELL = /usr/bin/env bash

.PHONY: default
default:
	@echo "see Makefile and README.md for help"
	@exit 2

.PHONY: run
run:
	pipenv run -- python -m sauna_bot

.PHONY: precommit
precommit: format typecheck

.PHONY: typecheck
typecheck:
	pipenv run -- mypy --ignore-missing-imports --strict-optional sauna_bot/

.PHONY: format
format:
	pipenv run -- black --py36 sauna_bot/

.PHONY: test 
test:
	pipenv run -- python -m pytest

.PHONY: formatcheck
formatcheck:
	pipenv run -- python -m black --py36 --check -q sauna_bot/ && echo "Code style check passed" || (echo "Code style check failed, try 'make format'" && false)

.PHONY: testall
testall: test formatcheck typecheck
