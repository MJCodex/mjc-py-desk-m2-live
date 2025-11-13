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
	$(PYTHON) -m src.web_api

buildexe:
	pyinstaller --onefile --windowed --add-data "src/ui;src/ui" --add-data "store;store" web_launcher.py