VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3
STREAMLIT = $(VENV)/bin/streamlit
UVICORN = $(VENV)/bin/uvicorn

# Need to use python 3.9 for aws lambda
$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

app: $(VENV)/bin/activate
	$(STREAMLIT) run app.py --server.port 8081

doc: $(VENV)/bin/activate
	$(PYTHON) doc_util.py

la: $(VENV)/bin/activate
	$(PYTHON) la_util.py

key: $(VENV)/bin/activate
	$(PYTHON) key_summary.py

clean:
	rm -rf __pycache__
	rm -rf $(VENV)