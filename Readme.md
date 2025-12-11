# RAG Service — Document Question Answering

## Overview
Short description of the project and features.

## Requirements
- Python 3.9+
- .env with OPENAI_API_KEY
- Install: `pip install -r requirements.txt`

## Run locally
```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
