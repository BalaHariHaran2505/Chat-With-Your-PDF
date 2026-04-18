# PDF Q&A System — Setup Guide for VS Code (Windows)

---

## Prerequisites

- Windows PC, 4 GB RAM minimum
- VS Code installed → https://code.visualstudio.com
- Python 3.11 installed → https://www.python.org/downloads/release/python-3119/
  - During install: check ✅ "Add Python to PATH"

---

## One-time Setup

### Step 1 — Open project in VS Code

1. Create a folder, e.g. `C:\Users\Hari\OneDrive\Desktop\NLP`
2. Place `app.py` and `requirements.txt` inside it
3. Open VS Code → File → Open Folder → select that folder

### Step 2 — Open the VS Code terminal

Press **Ctrl + `** (backtick) to open the integrated terminal

### Step 3 — Create a virtual environment with Python 3.11

```bash
py -3.11 -m venv venv
```

### Step 4 — Activate the virtual environment

```bash
venv\Scripts\activate
```

You should now see `(venv)` at the start of every terminal line.

### Step 5 — Install all dependencies

```bash
pip install -r requirements.txt
```

> First install takes 3–5 minutes. The embedding model (~90 MB) downloads automatically.

### Step 6 — Install Ollama

Download from: https://ollama.com/download/windows  
Run the installer. No configuration needed.

### Step 7 — Download TinyLlama (one time only, ~600 MB)

In the VS Code terminal:
```bash
ollama pull tinyllama
```

---

## Running the App (Every Time)

### Terminal 1 — Start Ollama

Open a **new terminal** (click the + icon in the VS Code terminal panel):
```bash
ollama serve
```
Leave this running. You should see: `Listening on 127.0.0.1:11434`

### Terminal 2 — Run the app

In the original terminal (with `(venv)` active):
```bash
python app.py
```

Your browser will open automatically at **http://127.0.0.1:7860**

---

## Using the App

```
1. Click "Upload PDF" → choose your PDF file
2. Click "⚙️ Process PDF" → wait for ✅ success message
3. Type your question in the text box
4. Click "Ask ↗" or press Enter
5. Read the answer (with source page numbers)
6. Keep asking — the chat history stays visible
```

---

## VS Code Tips

- Select Python interpreter: **Ctrl+Shift+P** → "Python: Select Interpreter" → choose the one with `venv`
- Split terminals: click the split icon in the terminal panel to run Ollama and the app side by side
- To stop the app: press **Ctrl+C** in Terminal 2

---

## Troubleshooting

| Error | Fix |
|---|---|
| `(venv)` not showing | Run `venv\Scripts\activate` again |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside venv |
| `Connection refused` | Run `ollama serve` in a separate terminal |
| `tinyllama not found` | Run `ollama pull tinyllama` |
| Browser doesn't open | Go to http://127.0.0.1:7860 manually |
| Still on Python 3.14 | Check with `python --version` — must be 3.11.x |
| Slow first question | Normal — TinyLlama loads into memory on first use |

---

## Folder Structure

```
NLP/
├── app.py              ← main application
├── requirements.txt    ← dependencies
├── README.md           ← this file
└── venv/               ← virtual environment (auto-created)
```

---

*Built with Gradio · LangChain · FAISS · HuggingFace · Ollama TinyLlama*
