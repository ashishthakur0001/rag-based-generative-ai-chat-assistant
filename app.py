import os
import re
from pathlib import Path
from typing import Dict, List

import chainlit as cl
import requests
from dotenv import load_dotenv
from pypdf import PdfReader


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "4"))


def read_pdf(path: str) -> List[Dict[str, str]]:
    reader = PdfReader(path)
    chunks = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        chunks.extend(chunk_text(text, f"{Path(path).name}, page {index}"))
    return chunks


def read_text(path: str) -> List[Dict[str, str]]:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return chunk_text(text, Path(path).name)


def chunk_text(text: str, source: str) -> List[Dict[str, str]]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []

    chunks = []
    start = 0
    while start < len(cleaned):
        end = start + CHUNK_SIZE
        chunks.append({"text": cleaned[start:end], "source": source})
        start = max(end - CHUNK_OVERLAP, end)
    return chunks


def load_files(files: List[str]) -> List[Dict[str, str]]:
    chunks = []
    for file_path in files:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            chunks.extend(read_pdf(file_path))
        elif suffix in {".txt", ".md"}:
            chunks.extend(read_text(file_path))
    return chunks


def tokenize(text: str) -> set:
    return {word for word in re.findall(r"[a-zA-Z0-9]{3,}", text.lower())}


def retrieve(question: str, chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
    query_terms = tokenize(question)
    ranked = []
    for chunk in chunks:
        chunk_terms = tokenize(chunk["text"])
        score = len(query_terms & chunk_terms)
        if score:
            ranked.append((score, chunk))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in ranked[:TOP_K]] or chunks[:TOP_K]


def call_groq(question: str, context_chunks: List[Dict[str, str]], history: List[Dict[str, str]]) -> str:
    if not GROQ_API_KEY:
        return (
            "The app is running, but GROQ_API_KEY is missing. "
            "Create a .env file with GROQ_API_KEY=your_key_here, then restart the app."
        )

    context = "\n\n".join(
        f"Source: {chunk['source']}\n{chunk['text']}" for chunk in context_chunks
    )
    recent_history = history[-6:]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful RAG document assistant. Answer using only the provided context. "
                "If the answer is not present in the context, say you do not know from the uploaded documents. "
                "Keep the answer clear and include source names when useful."
            ),
        }
    ]
    messages.extend(recent_history)
    messages.append(
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        }
    )

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.1,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def source_list(chunks: List[Dict[str, str]]) -> str:
    seen = []
    for chunk in chunks:
        if chunk["source"] not in seen:
            seen.append(chunk["source"])
    return "\n".join(f"- {source}" for source in seen)


@cl.on_chat_start
async def start():
    cl.user_session.set("chunks", [])
    cl.user_session.set("history", [])
    cl.user_session.set("last_sources", [])
    await cl.Message(
        content=(
            "Upload PDF, TXT, or MD files to start. "
            "Commands: `/summary`, `/sources`, `/reset`."
        )
    ).send()


@cl.on_message
async def main(message: cl.Message):
    if message.elements:
        files = [
            element.path
            for element in message.elements
            if Path(element.name or element.path).suffix.lower() in {".pdf", ".txt", ".md"}
        ]
        if not files:
            await cl.Message(content="Please upload PDF, TXT, or MD files only.").send()
            return

        chunks = load_files(files)
        cl.user_session.set("chunks", chunks)
        cl.user_session.set("history", [])
        cl.user_session.set("last_sources", [])
        await cl.Message(content=f"Processed {len(files)} file(s) into {len(chunks)} text chunks.").send()
        return

    command = message.content.strip().lower()
    if command == "/reset":
        cl.user_session.set("chunks", [])
        cl.user_session.set("history", [])
        cl.user_session.set("last_sources", [])
        await cl.Message(content="Session reset. Upload a document to begin again.").send()
        return

    if command == "/sources":
        sources = cl.user_session.get("last_sources") or []
        await cl.Message(content=source_list(sources) if sources else "No sources yet.").send()
        return

    chunks = cl.user_session.get("chunks") or []
    if not chunks:
        await cl.Message(content="Please upload a PDF, TXT, or MD file first.").send()
        return

    question = "Summarize the uploaded document." if command == "/summary" else message.content
    selected = retrieve(question, chunks)
    cl.user_session.set("last_sources", selected)

    try:
        answer = call_groq(question, selected, cl.user_session.get("history") or [])
    except Exception as exc:
        await cl.Message(content=f"Could not call Groq: {exc}").send()
        return

    history = cl.user_session.get("history") or []
    history.extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ])
    cl.user_session.set("history", history)

    await cl.Message(content=f"{answer}\n\nSources:\n{source_list(selected)}").send()
