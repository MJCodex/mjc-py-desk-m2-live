# Variables
PYTHON=python
PIP=pip
VENV=venv

# Reglas
install:
ifeq ($(OS),Windows_NT)
	$(PYTHON) -m venv $(VENV)
	$(VENV)\Scripts\activate && $(PIP) install -r requirements.txt
else
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
endif

run:
	$(PYTHON) detector.py

buildexe:
	pyinstaller -w --onefile --add-data "store;store" --add-data "src;src" detector.py