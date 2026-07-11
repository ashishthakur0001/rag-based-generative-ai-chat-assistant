import os
import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Dict, List

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pypdf import PdfReader


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "4"))

app = FastAPI(title="RAG Document Chatbot")
SESSIONS: Dict[str, Dict[str, List[Dict[str, str]]]] = {}


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>RAG Document Chatbot</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, system-ui, -apple-system, Segoe UI, sans-serif; }
    body { margin: 0; background: #101418; color: #edf2f7; }
    main { width: min(980px, calc(100vw - 32px)); margin: 0 auto; padding: 28px 0; }
    header { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 20px; }
    h1 { font-size: clamp(28px, 5vw, 44px); margin: 0; }
    .status { color: #8ee6c4; font-size: 14px; }
    .panel { border: 1px solid #2c3640; border-radius: 8px; background: #161c22; padding: 16px; }
    .upload { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }
    input[type=file] { flex: 1; min-width: 240px; }
    button { border: 0; border-radius: 6px; padding: 11px 14px; background: #2f81f7; color: white; cursor: pointer; font-weight: 700; }
    button:disabled { background: #53606d; cursor: not-allowed; }
    #chat { height: min(58vh, 560px); overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding: 4px; }
    .msg { max-width: 82%; padding: 12px 14px; border-radius: 8px; white-space: pre-wrap; line-height: 1.45; }
    .user { align-self: flex-end; background: #263d5c; }
    .bot { align-self: flex-start; background: #202832; border: 1px solid #2c3640; }
    .composer { display: flex; gap: 10px; margin-top: 14px; }
    textarea { flex: 1; min-height: 46px; max-height: 140px; resize: vertical; border-radius: 6px; border: 1px solid #33404c; background: #0f1419; color: #edf2f7; padding: 12px; }
    .hint { color: #a7b4c2; font-size: 13px; margin-top: 10px; }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>RAG Document Chatbot</h1>
        <div class="hint">Upload a PDF, TXT, or MD file, then ask questions from the document.</div>
      </div>
      <div class="status" id="status">Ready</div>
    </header>
    <section class="panel">
      <div class="upload">
        <input id="file" type="file" accept=".pdf,.txt,.md" multiple />
        <button id="upload">Upload</button>
      </div>
      <div id="chat"></div>
      <div class="composer">
        <textarea id="message" placeholder="Ask a question, or type /summary"></textarea>
        <button id="send" disabled>Send</button>
      </div>
      <div class="hint">Commands: /summary, /reset</div>
    </section>
  </main>
  <script>
    let sessionId = null;
    const chat = document.getElementById("chat");
    const statusEl = document.getElementById("status");
    const sendBtn = document.getElementById("send");
    const messageEl = document.getElementById("message");

    function addMessage(text, type) {
      const div = document.createElement("div");
      div.className = `msg ${type}`;
      div.textContent = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    document.getElementById("upload").onclick = async () => {
      const files = document.getElementById("file").files;
      if (!files.length) return addMessage("Choose at least one file first.", "bot");
      const form = new FormData();
      for (const file of files) form.append("files", file);
      statusEl.textContent = "Processing...";
      const res = await fetch("/upload", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) {
        statusEl.textContent = "Upload failed";
        return addMessage(data.detail || "Upload failed.", "bot");
      }
      sessionId = data.session_id;
      sendBtn.disabled = false;
      statusEl.textContent = "Documents ready";
      addMessage(data.message, "bot");
    };

    async function send() {
      const message = messageEl.value.trim();
      if (!message || !sessionId) return;
      if (message === "/reset") {
        sessionId = null;
        sendBtn.disabled = true;
        chat.innerHTML = "";
        statusEl.textContent = "Ready";
        messageEl.value = "";
        return;
      }
      addMessage(message, "user");
      messageEl.value = "";
      statusEl.textContent = "Thinking...";
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message })
      });
      const data = await res.json();
      statusEl.textContent = "Documents ready";
      addMessage(res.ok ? data.answer : (data.detail || "Request failed."), "bot");
    }

    sendBtn.onclick = send;
    messageEl.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        send();
      }
    });
  </script>
</body>
</html>
"""


class ChatRequest(BaseModel):
    session_id: str
    message: str


def chunk_text(text: str, source: str) -> List[Dict[str, str]]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []

    chunks = []
    step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
    for start in range(0, len(cleaned), step):
        chunks.append({"text": cleaned[start : start + CHUNK_SIZE], "source": source})
    return chunks


async def read_upload(file: UploadFile) -> List[Dict[str, str]]:
    suffix = Path(file.filename or "").suffix.lower()
    data = await file.read()

    if suffix == ".pdf":
        reader = PdfReader(BytesIO(data))
        chunks = []
        for index, page in enumerate(reader.pages, start=1):
            chunks.extend(chunk_text(page.extract_text() or "", f"{file.filename}, page {index}"))
        return chunks

    if suffix in {".txt", ".md"}:
        return chunk_text(data.decode("utf-8", errors="ignore"), file.filename or "uploaded file")

    raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files are supported.")


def tokenize(text: str) -> set:
    return {word for word in re.findall(r"[a-zA-Z0-9]{3,}", text.lower())}


def retrieve(question: str, chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
    query_terms = tokenize(question)
    ranked = []
    for chunk in chunks:
        score = len(query_terms & tokenize(chunk["text"]))
        if score:
            ranked.append((score, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in ranked[:TOP_K]] or chunks[:TOP_K]


def source_list(chunks: List[Dict[str, str]]) -> str:
    seen = []
    for chunk in chunks:
        if chunk["source"] not in seen:
            seen.append(chunk["source"])
    return "\n".join(f"- {source}" for source in seen)


def call_groq(question: str, context_chunks: List[Dict[str, str]], history: List[Dict[str, str]]) -> str:
    if not GROQ_API_KEY:
        return "GROQ_API_KEY is missing. Add it in Render environment variables, then redeploy."

    context = "\n\n".join(f"Source: {chunk['source']}\n{chunk['text']}" for chunk in context_chunks)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful RAG document assistant. Answer using only the provided context. "
                "If the answer is not in the context, say you do not know from the uploaded documents."
            ),
        },
        *history[-6:],
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.1},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)) -> Dict[str, str]:
    chunks = []
    for file in files:
        chunks.extend(await read_upload(file))

    if not chunks:
        raise HTTPException(status_code=400, detail="No readable text was found in the uploaded files.")

    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"chunks": chunks, "history": []}
    return {
        "session_id": session_id,
        "message": f"Processed {len(files)} file(s) into {len(chunks)} chunks. Ask your questions now.",
    }


@app.post("/chat")
def chat(request: ChatRequest) -> Dict[str, str]:
    session = SESSIONS.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Upload the documents again.")

    question = "Summarize the uploaded document." if request.message.strip().lower() == "/summary" else request.message
    selected = retrieve(question, session["chunks"])
    answer = call_groq(question, selected, session["history"])
    session["history"].extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ])

    return {"answer": f"{answer}\n\nSources:\n{source_list(selected)}"}
