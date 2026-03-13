# app/Makefile

.PHONY: install playground test eval

install:
	uv sync

playground:
	uv run adk web .

test:
	uv run pytest tests/

eval:
	uv run adk eval . ../eval/eval_cases.json
