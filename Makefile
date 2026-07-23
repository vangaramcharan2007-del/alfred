# Makefile for Jarvis X

.PHONY: install run test clean lint check diagnose

install:
	python scripts/bootstrap.py

run:
	python jarvis.py

test:
	pytest tests/ -v --cov=src/jarvisx

clean:
	python -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('.pytest_cache', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('logs', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('databases', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('workspace', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('vault', ignore_errors=True)"
	python -c "import shutil; shutil.rmtree('memory', ignore_errors=True)"

diagnose:
	python scripts/diagnose.py

check: test diagnose
