<div align="center">

# 🤖 RAG Document Chatbot

### Chat with your documents using Retrieval-Augmented Generation

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ashishthakur0001/rag-based-generative-ai-chat-assistant)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Chainlit](https://img.shields.io/badge/UI-Chainlit-F97316)
![Groq](https://img.shields.io/badge/LLM-Groq-00A67E)
![License](https://img.shields.io/badge/License-MIT-4CAF50)

</div>

---

## 📖 Overview

**RAG Document Chatbot** is a Generative AI application that turns static documents into a conversational knowledge base. Upload a PDF, TXT, or Markdown file, ask a question in plain English, and the assistant retrieves the most relevant passages and uses a large language model to generate a grounded, source-cited answer — instead of hallucinating from memory.

It's built on the **Retrieval-Augmented Generation (RAG)** pattern:

> **Documents → Chunks → Retrieval → LLM Context → Grounded Answer**

This is the same architectural pattern behind production tools like internal knowledge-base assistants, customer support copilots, and document Q&A systems — implemented here as a clean, self-contained, deployable reference project.

---

## ✨ What It Can Do

| Capability | Description |
|---|---|
| 📄 **Multi-format ingestion** | Upload and parse PDF, TXT, and Markdown files |
| 📚 **Multi-document sessions** | Combine multiple files into a single searchable knowledge base per session |
| 🔍 **Context retrieval** | Uses lightweight keyword-based search to surface the most relevant chunks for each question |
| 🧠 **LLM-powered answers** | Sends retrieved context to a Groq-hosted LLM to generate accurate, grounded responses |
| 💬 **Conversational memory** | Remembers recent turns in the conversation for natural follow-up questions |
| 🔗 **Source attribution** | Every answer lists the exact document(s) it was drawn from |
| ⚡ **Slash commands** | `/summary` — summarize uploaded docs · `/sources` — show sources for the last answer · `/reset` — clear the session |

---

## 🏗️ How It Works

```
 ┌──────────────┐    ┌───────────────┐    ┌────────────────────┐    ┌──────────────────┐
 │  Upload Docs  │ →  │  Chunk Text   │ →  │  Retrieve Relevant │ →  │  Groq LLM         │
 │ (PDF/TXT/MD)  │    │ (with overlap)│    │  Chunks (Top-K)    │    │  Generates Answer │
 └──────────────┘    └───────────────┘    └────────────────────┘    │  + Cites Sources  │
                                                                     └──────────────────┘
```

1. **Ingestion** — Documents are parsed and cleaned.
2. **Chunking** — Text is split into overlapping segments (configurable size/overlap) so context isn't lost at chunk boundaries.
3. **Retrieval** — Each question is matched against all chunks using keyword scoring; the top-K most relevant chunks are selected.
4. **Generation** — The selected chunks and recent chat history are passed to a Groq-hosted LLM, instructed to answer strictly from the given context.
5. **Response** — The model's answer is returned to the user along with the source documents used, so answers stay verifiable.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Chat Interface | [Chainlit](https://chainlit.io) | Interactive web-based chat UI |
| LLM Inference | [Groq API](https://groq.com) | Fast hosted inference for the response-generation model |
| PDF Parsing | [PyPDF](https://pypi.org/project/pypdf/) | Extracts text from uploaded PDF files |
| HTTP Layer | [Requests](https://pypi.org/project/requests/) | Communicates with the Groq API |
| Configuration | [python-dotenv](https://pypi.org/project/python-dotenv/) | Loads environment variables from `.env` |
| Runtime | Python 3.11 | Core application language |
| Hosting | Render | One-click cloud deployment |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/ashishthakur0001/rag-based-generative-ai-chat-assistant.git
cd rag-based-generative-ai-chat-assistant
```

### 2. Configure environment variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

### 3. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run the app
```bash
python -m chainlit run app.py --host 127.0.0.1 --port 8000
```

**Windows shortcut:**
```bat
setup.bat
Run.bat
```

Once running, open your browser to `http://127.0.0.1:8000`, upload a document, and start asking questions.

---

## ⚙️ Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Your Groq API key (required for answer generation) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Which Groq-hosted model to use |
| `CHUNK_SIZE` | `1200` | Character length of each text chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between consecutive chunks, to preserve context continuity |
| `TOP_K` | `4` | Number of chunks retrieved per question |

---

## ☁️ Deployment

This project is pre-configured for one-click deployment on **Render**.

**Start command:**
```bash
python -m chainlit run app.py --host 0.0.0.0 --port $PORT --headless
```

**Environment variables to set on Render:**
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

`Procfile` and `render.yaml` are already included, so deployment requires no extra configuration beyond your API key.

---

## 📁 Project Structure

```
.
├── app.py              # Core logic — chunking, retrieval, Groq calls, Chainlit event hooks
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── chainlit.md          # Chainlit welcome screen content
├── render.yaml           # Render deployment configuration
├── Procfile               # Process definition for deployment
├── runtime.txt            # Pinned Python version
├── setup.bat / Run.bat    # Windows setup & run helper scripts
├── .env.example            # Sample environment variable file
└── .gitignore
```

---

## 🖼️ Screenshots

> Add screenshots once deployed, referencing them like below:

```markdown
![Upload Screen](docs/screenshot-upload.png)
![Chat in Action](docs/screenshot-chat.png)
![Source Attribution](docs/screenshot-sources.png)
```

---

## 📝 Notes

- A valid `GROQ_API_KEY` is required for the assistant to generate answers.
- Without a key, the UI still loads normally, but responses will display a clear "missing API key" message instead of failing silently.
- Retrieval currently relies on keyword-based scoring rather than embedding-based semantic search, keeping the project dependency-light and fast to set up locally.

---

## 🧩 Roadmap

- [ ] Upgrade retrieval to embedding-based semantic search (e.g., `sentence-transformers` + Chroma/FAISS)
- [ ] Add support for `.docx` and `.csv` uploads
- [ ] Persist documents and chat history across sessions
- [ ] Add automated tests for chunking and retrieval logic

---

## 📄 About

This project explores a practical, production-style Retrieval-Augmented Generation pipeline — transforming unstructured documents into a queryable knowledge source and grounding LLM output in real content rather than the model's raw memory. It's designed to be minimal, easy to run locally, and quick to deploy.

---

## 📜 License

Licensed under the **MIT License**. You are free to use, modify, and distribute this project with attribution. See [LICENSE](LICENSE) for full terms.

---

<div align="center">

**Author:** [Ashish Thakur](https://github.com/ashishthakur0001)

</div>
