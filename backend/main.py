from fastapi import FastAPI, HTTPException, Request
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json

app = FastAPI()
qdrant = QdrantClient(url="http://host.docker.internal:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this later, e.g. ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.post("/ingest_json")
# async def ingest(request: Request):
#     data = await request.json()
def ingest():
    file_path = os.path.join(os.path.dirname(__file__), "../scene_export.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    nodes = data["nodes"]
    texts = [
        f"Name: {node['name']}, Class: {node['class_']}, Material: {node['material']}, "
        f"Subsystem: {node['user_props'].get('Subsystem', '')}, Weight: {node['user_props'].get('Weight', '')} "
        for node in nodes
    ]

    embeddings = model.encode(texts)

    qdrant.recreate_collection(
        collection_name="scene_objects",
        vectors_config={"size": len(embeddings[0]), "distance": "Cosine"},
    )

    qdrant.upsert(
        collection_name="scene_objects",
        points=[
            {"id": i, "vector": emb.tolist(), "payload": node}
            for i, (emb, node) in enumerate(zip(embeddings, nodes))
        ],
    )

    return {"status": "ok", "count": len(texts)}


print("[INFO] Running initial ingestion...")
try:
    result = ingest()
    print(f"[INFO] Ingested {result['count']} nodes into Qdrant.")
except Exception as e:
    print(f"[WARN] Ingestion failed: {e}")


@app.post("/stream_query")
async def stream_query(request: Request):
    data = await request.json()
    query = data.get("query")
    query_vec = model.encode(query).tolist()
    results = qdrant.search(
        collection_name="scene_objects", query_vector=query_vec, limit=3
    )

    context = "\n".join(str(r.payload) for r in results)

    prompt = f"Scene Info:\n{context}\n\nQuestion:\n{query}\n\nAnswer: \n"

    try:
        response = requests.post(
            "http://ollama:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Ollama request failed: {e}")

    output = response.json()
    answer = output.get("response", "")

    return {"answer": answer, "matches": [r.payload for r in results]}


static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
