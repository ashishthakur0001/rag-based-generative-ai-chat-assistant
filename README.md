# RAG Document Chatbot



**Live Demo:** [https://rag-document-chatbot-z3pa.onrender.com](https://rag-document-chatbot-z3pa.onrender.com)

RAG Document Chatbot is a Generative AI application that lets users upload PDF, TXT, or Markdown files and ask questions about their content. It retrieves relevant document chunks and sends them to a Groq-hosted large language model to generate grounded answers with source references.

## Features

- Upload PDF, TXT, and Markdown files.
- Ask questions from uploaded documents.
- Multi-document sessions.
- Lightweight keyword-based retrieval.
- Groq LLM answer generation.
- Recent chat memory.
- Source references in responses.
- `/summary` command for document summaries.
- `/reset` command to clear the current browser session.

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- Groq API
- PyPDF
- Requests
- Render

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/ashishthakur0001/rag-based-generative-ai-chat-assistant.git
cd rag-based-generative-ai-chat-assistant
```

2. Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Run locally:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

On Windows, you can also run:

```bat
setup.bat
Run.bat
```

## Render Deployment

This repo includes `render.yaml`, so Render can deploy it as a Blueprint.

Build command:

```bash
python -m pip install -r requirements.txt
```

Start command:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | required | Groq API key for answer generation |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Groq model name |
| `CHUNK_SIZE` | `1200` | Character length of each text chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `TOP_K` | `4` | Number of chunks retrieved per question |

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- Requirement.txt
|-- README.md
|-- render.yaml
|-- Procfile
|-- runtime.txt
|-- setup.bat
|-- Run.bat
|-- .env.example
`-- .gitignore
```

## Notes

- A valid `GROQ_API_KEY` is required for generated answers.
- Without `GROQ_API_KEY`, the web app still loads and shows a clear missing-key message.
- Retrieval currently uses keyword scoring to keep deployment lightweight.
