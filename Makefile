PYTHON=.venv/bin/python

.PHONY: build install

install: requirements.txt
	$(PYTHON) -m pip install -r $^

build: build-svg.py template.svg
	$(PYTHON) $<
	git add '*.svg' && \
	GIT_AUTHOR_NAME='publicmatt' GIT_AUTHOR_EMAIL='git@publicmatt.com' \
	GIT_COMMITTER_NAME='publicmatt' GIT_COMMITTER_EMAIL='git@publicmatt.com' \
	git commit -m "Auto-updating git readme"
	git push publicmatt
	git push github

