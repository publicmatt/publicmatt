PYTHON=.venv/bin/python

.PHONY: build install commit

all: build commit

install: requirements.txt
	$(PYTHON) -m pip install -r $^

build: build-svg.py template.svg
	$(PYTHON) $<

commit: chat.svg
	git add '*.svg' && \
	GIT_AUTHOR_NAME='publicmatt' GIT_AUTHOR_EMAIL='git@publicmatt.com' \
	GIT_COMMITTER_NAME='publicmatt' GIT_COMMITTER_EMAIL='git@publicmatt.com' \
	git commit -m "Auto-updating git readme"
	git push publicmatt
	git push github

