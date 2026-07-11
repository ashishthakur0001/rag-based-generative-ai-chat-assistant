# RAG Document Chatbot

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ashishthakur0001/rag-based-generative-ai-chat-assistant)

This is a Generative AI project. It uses Retrieval-Augmented Generation (RAG): uploaded documents are split into searchable chunks, relevant chunks are retrieved for each question, and a Groq-hosted large language model generates the final answer.

## What It Can Do

- Chat with uploaded PDF, TXT, and MD files.
- Support multiple document uploads in one session.
- Retrieve relevant context with lightweight keyword search.
- Generate answers using Groq LLMs.
- Keep conversational memory during the session.
- Show source references for answers.
- Use advanced commands:
  - `/summary` summarizes the uploaded documents.
  - `/sources` shows the sources from the last answer.
  - `/reset` clears the current session.

## Tech Stack

- Python
- Chainlit for the chat UI
- Groq for LLM response generation
- PyPDF for PDF loading
- Requests for calling the Groq API

## Setup

1. Create a `.env` file in this folder:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the app:

```bash
python -m chainlit run app.py --host 127.0.0.1 --port 8000
```

On Windows, you can also run:

```bat
setup.bat
Run.bat
```

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- Requirement.txt
|-- README.md
|-- Run.bat
|-- setup.bat
|-- render.yaml
|-- Procfile
|-- runtime.txt
|-- .env.example
`-- .gitignore
```

## Deployment

This project is ready for Render. Use this start command:

```bash
python -m chainlit run app.py --host 0.0.0.0 --port $PORT --headless
```

Set these environment variables on Render:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

## Notes

- The app needs a valid Groq API key to generate answers.
- Without `GROQ_API_KEY`, the UI still opens, but answers will show a missing-key message.
