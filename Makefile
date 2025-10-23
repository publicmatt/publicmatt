PYTHON=.venv/bin/python

.PHONY: build install commit

all: build commit

install: requirements.txt
	uv sync

build: app.py template.svg
	uv run app.py

commit: chat.svg
	git add '*.svg' && \
	GIT_AUTHOR_NAME='publicmatt' GIT_AUTHOR_EMAIL='git@publicmatt.com' \
	GIT_COMMITTER_NAME='publicmatt' GIT_COMMITTER_EMAIL='git@publicmatt.com' \
	git commit -m "auto-updating git readme"
	git push

