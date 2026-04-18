"""
Offline PDF Question Answering System
RAG: PyPDF → Chunks → FAISS → llama3.2
Both modes focus on PDF. PDF+AI reasons deeper from PDF context.
"""

import gradio as gr
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama

chunks   = []
index    = None
embedder = None

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(p.extract_text() for p in reader.pages if p.extract_text())

def split_text(text, chunk_size=100, overlap=20):
    words = text.split()
    result, i = [], 0
    while i < len(words):
        result.append(" ".join(words[i:i + chunk_size]))
        i += chunk_size - overlap
    return result

def build_faiss(text_chunks, model):
    emb = np.array(model.encode(text_chunks, show_progress_bar=False)).astype("float32")
    idx = faiss.IndexFlatL2(emb.shape[1])
    idx.add(emb)
    return idx

def retrieve(question, k=3):
    q = embedder.encode([question]).astype("float32")
    _, ids = index.search(q, k)
    return [chunks[i] for i in ids[0] if i < len(chunks)]

def generate(prompt):
    """Non-streaming call — returns full answer string."""
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0, "num_predict": 300},
    )
    return response["message"]["content"].strip()

def get_answer(question, top_chunks, mode):
    context = "\n".join(top_chunks)

    if mode == "📄 PDF Strict Mode":
        prompt = (
            f"Read the document carefully and answer the question using ONLY "
            f"information from the document.\n"
            f"If the answer is not in the document, say: Not found in document\n\n"
            f"Document:\n{context}\n\n"
            f"Question: {question}\n"
            f"Short direct answer:"
        )
    else:
        # PDF + AI Mode: focus on PDF, use AI to reason/infer from it
        prompt = (
            f"You are an expert assistant. Read the document and answer the question.\n"
            f"Use the document as your primary source.\n"
            f"If the exact answer is not stated, REASON and INFER from what the document says.\n"
            f"Give a helpful, complete answer based on the document content.\n\n"
            f"Document:\n{context}\n\n"
            f"Question: {question}\n"
            f"Answer:"
        )
    return generate(prompt)

def process_pdf(pdf_path):
    global chunks, index, embedder
    if pdf_path is None:
        yield "⚠️ Please upload a PDF file first."
        return
    try:
        yield "⏳ Extracting text..."
        text = extract_text(pdf_path)
        if not text.strip():
            yield "❌ Could not extract text."
            return
        yield "⏳ Building search index..."
        chunks = split_text(text)
        if embedder is None:
            embedder = SentenceTransformer("all-MiniLM-L6-v2")
        index = build_faiss(chunks, embedder)
        yield f"✅ Ready! {len(chunks)} chunks. Ask your questions!"
    except Exception as e:
        yield f"❌ Error: {str(e)}"

def answer_question(question, history, mode):
    history = history or []
    if not question.strip():
        return history, ""
    if index is None:
        history.append({"role": "user",      "content": question})
        history.append({"role": "assistant", "content": "⚠️ Please upload and process a PDF first."})
        return history, ""

    history.append({"role": "user",      "content": question})
    history.append({"role": "assistant", "content": "⏳ Thinking..."})
    yield history, ""

    try:
        top_chunks  = retrieve(question, k=3)
        answer      = get_answer(question, top_chunks, mode)
        history[-1] = {"role": "assistant", "content": answer}
        yield history, ""
    except Exception as e:
        msg = "❌ Ollama not running. Run: ollama serve" \
              if "connection" in str(e).lower() or "refused" in str(e).lower() \
              else f"❌ Error: {str(e)}"
        history[-1] = {"role": "assistant", "content": msg}
        yield history, ""

with gr.Blocks(title="PDF Q&A") as app:
    gr.Markdown("# 🧠 Chat With Your PDF\n### Ask anything. Get answers. No cloud. No API key. 100% private.")
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1. Upload PDF")
            pdf_input   = gr.File(label="PDF File", file_types=[".pdf"], type="filepath")
            process_btn = gr.Button("⚙️ Process PDF", variant="primary")
            status_box  = gr.Textbox(label="Status", lines=4, interactive=False)
            gr.Markdown(
                "**📄 PDF Strict:**\n"
                "Answers only what is written in the PDF.\n\n"
                "**🤖 PDF + AI:**\n"
                "Reads the PDF and reasons deeper — good for complex questions like "
                "'Is he eligible for my company?'"
            )
        with gr.Column(scale=2):
            gr.Markdown("### 2. Ask Questions")
            mode_toggle = gr.Radio(
                choices=["📄 PDF Strict Mode", "🤖 PDF + AI Mode"],
                value="📄 PDF Strict Mode",
                label="Answer Mode",
                info="Strict: exact answers from PDF  |  PDF + AI: AI reasons from PDF for complex questions",
            )
            chatbot        = gr.Chatbot(label="Chat", height=420)
            question_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. Is he eligible for an AI company?",
                lines=2
            )
            with gr.Row():
                ask_btn   = gr.Button("Ask ↗", variant="primary")
                clear_btn = gr.Button("🗑️ Clear", variant="secondary")

    process_btn.click(fn=process_pdf, inputs=[pdf_input], outputs=[status_box])
    ask_btn.click(fn=answer_question, inputs=[question_input, chatbot, mode_toggle], outputs=[chatbot, question_input])
    question_input.submit(fn=answer_question, inputs=[question_input, chatbot, mode_toggle], outputs=[chatbot, question_input])
    clear_btn.click(fn=lambda: ([], ""), outputs=[chatbot, question_input])

if __name__ == "__main__":
    print("\n========================================")
    print("  PDF Q&A — starting...")
    print("========================================\n")
    app.launch(inbrowser=True)