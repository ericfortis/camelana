build: clean
	.venv/bin/python camelize.py

clean:
	rm -f *.ttf

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install fonttools

replace-fea:
	.venv/bin/python replace_fea.py

debug-fea:
	.venv/bin/python debug_fea.py

.PHONY: *
