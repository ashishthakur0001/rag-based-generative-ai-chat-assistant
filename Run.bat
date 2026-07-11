@echo off

echo Starting RAG Chatbot...

set DEBUG=
python -m chainlit run app.py --host 127.0.0.1 --port 8000

pause
