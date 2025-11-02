# 📚 Telegram study bot

## Project Overview

The **Telegram study bot** is a comprehensive Telegram bot designed to be an intelligent study assistant. It automates the process of accessing, downloading, and studying university notes by combining robust **web scraping** with an advanced **Retrieval-Augmented Generation (RAG)** system.

The primary goal is to provide a reliable source of truth directly from verified study material, effectively eliminating AI "hallucination" by grounding responses in a local knowledge base.

---
## project structure
```

telegram-study-bot
├── src
│   ├── telegram_bot.py       # Main logic for the Telegram bot
│   ├── scraper.py            # Web scraper for downloading study materials
│   └── rag.py                # Handles retrieval-augmented generation (RAG)
├── data
│   ├── chroma_store/         # Persistent ChromaDB Vector Database files
│   ├── downloaded_notes/     # Temporary folder for downloaded PDFs
│   └── .gitignore            # Ensures data is IGNORED by Git (CRITICAL)
├── .env.example              # Example environment variables configuration
└── requirements.txt          # Python dependencies
```
## 🚀 Key Features

* **Guided Access:** Uses interactive inline menus for Branch → Semester → Subject selection.
* **Structured Scraping:** Employs **PyMuPDF4LLM** for superior text extraction that preserves tables and headings.
* **Smart Downloading:** Scrapes dynamic Google Drive preview links and converts them to **direct download URLs** to retrieve the correct PDF file content.
* **Vectorized Knowledge Base:** Builds a persistent knowledge base using **ChromaDB** and **HuggingFace Embeddings**.
* **Dynamic Q&A:** Answers questions using the **DeepSeek Chat LLM** (via OpenRouter), grounded exclusively in the stored notes.
* **Resource Management:** Automatically deletes downloaded PDF files from the server after they are successfully processed and stored in the database.

---

## 🛠️ Technology Stack

| Category | Component | Python Package | Purpose |
| :--- | :--- | :--- | :--- |
| **Bot Framework** | Main Application | `python-telegram-bot` | Handles all commands, callbacks, and file transfer. |
| **PDF Processing** | Structure Extraction | `pymupdf4llm` | Extracts text/tables in structured Markdown format. |
| **Web Scraping** | Network/Parsing | `requests`, `BeautifulSoup` | Fetches HTML and parses subject links. |
| **Vector Database** | Storage/Indexing | `chromadb`, `sentence-transformers` | Stores and indexes the numerical embeddings of the notes. |
| **RAG Orchestration**| LLM Integration | `openai`, `python-dotenv` | Manages the API connection to DeepSeek (via OpenRouter) for generation. |

---

## ⚙️ Installation and Setup

### Prerequisites
1.  **Python 3.10+** and **Git** installed locally.
2.  **API Keys:** Telegram Bot Token (from @BotFather) and OpenRouter API Key.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd Telegram_Study_Bot
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in the required values.

## Usage
1. Run the bot:
   ```
   python src/telegram_bot.py
   ```

2. Interact with the bot on Telegram using the commands:
   - `/start` - Start the bot and see the main menu.
   - `/help` - Show the help message.
   - `/notes` - Initiates the menu for Branch/Semester selection, downloads the PDFs, and sends them to the chat.
   - `/store` - Processes all downloaded notes, extracts the vectors, stores them in ChromaDB.
   - `/ask <question>` - Ask a question about your materials.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
