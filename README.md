# 🛰️ Spatial Intelligence Assistant  
*A Retrieval-Augmented AI Assistant for 3D Design Environments*

---

## 🚀 Overview

**Spatial Intelligence Assistant** is an intelligent 3D design companion that lets users query their **3ds Max** scenes in natural language and receive context-aware responses.  
It combines **scene understanding**, **semantic search**, and **LLM reasoning** in a fully local, Dockerized Retrieval-Augmented Generation (RAG) system.

Example queries:
> “Highlight all propulsion components.”  
> “What is the total mass of the solar modules?”  

---

## 🧠 Architecture

3ds Max (Python)
↓ [scene metadata JSON]
FastAPI Backend (Docker)
├─ SentenceTransformers → embeddings
├─ Qdrant → vector storage & retrieval
└─ Mistral-7B (Ollama) → contextual generation
↓
3ds Max Visualization
→ highlight objects & print summary

| Layer | Technology | Role |
|--------|-------------|------|
| **3D Layer** | 3ds Max Python (`pymxs`) | Extracts metadata & renders highlights |
| **API Layer** | FastAPI | Endpoints `/ingest` and `/query` |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) | Text → vector encoding |
| **Vector DB** | Qdrant (Docker) | Semantic storage + filtering |
| **LLM Engine** | Mistral 7B (Ollama) | Context-aware reasoning |
| **Containerization** | Docker / Compose | Reproducible local deployment |
| **Optional Framework** | LangChain | High-level RAG orchestration |

---

## 🔄 Data Flow

1. **Scene Metadata Extraction**  
   Python in 3ds Max iterates through objects (`pymxs`), collects attributes  
   *(name, material, type, position, etc.)*, and sends them via POST to `/ingest`.

2. **Embedding + Storage**  
   Backend uses SentenceTransformers to embed descriptions and stores vectors + metadata in **Qdrant**.

3. **User Query**  
   Designer types a natural-language question in the 3ds Max UI → POST `/query`.

4. **Retrieval (R in RAG)**  
   Query embedding is matched semantically against stored vectors in Qdrant (with optional filters).

5. **Generation (AG in RAG)**  
   Retrieved context is injected into a prompt for **Mistral**, which produces a grounded answer and a list of related objects.

6. **Visualization + Response**  
   3ds Max script highlights returned objects and prints the textual explanation inside the viewport or console.

---

## 🧩 Key Features

- **End-to-End Local:** all components run on-premise (ideal for restricted data).  
- **Modular Design:** swap FAISS ↔ Qdrant or Mistral ↔ Llama ↔ GPT-4 easily.  
- **Scalable Storage:** Qdrant handles large collections with metadata filters (`type="solar"`, `mass<100`).  
- **Bilingual-Ready:** extend embeddings for English / French input.  
- **Future-Proof:** LangChain integration available for memory and multi-model expansion.

---

## 🧱 Example Interaction

**User:** “Show me all solar components lighter than 100 kg.”  

**Backend Flow**
1. Embed query → Qdrant vector search + filter (`type="solar"`, `mass<100`).  
2. Retrieve context → pass to Mistral for summary.  

**Response**
```json
{
  "answer": "Solar modules include Panel_A and Panel_B (total 84 kg).",
  "highlight": ["Panel_A", "Panel_B"]
}
3ds Max Output

Panels highlight in the viewport.

Text printed: “Solar modules include Panel_A and Panel_B (total 84 kg).”
