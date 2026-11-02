import os

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from db import connect, find_nearest, insert_entry

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = connect()

THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))


class EmbedRequest(BaseModel):
    text: str


class SearchRequest(BaseModel):
    prompt: str


class StoreRequest(BaseModel):
    prompt: str
    response: str
    model: str


@app.get("/health")
def health():
    return {"status": "ok", "dimensions": 384, "threshold": THRESHOLD}


@app.post("/embed")
def embed(req: EmbedRequest):
    vector = model.encode(req.text)
    return {"vector": vector.tolist(), "dimensions": len(vector)}


@app.post("/search")
def search(req: SearchRequest):
    embedding = model.encode(req.prompt)
    rows = find_nearest(conn, embedding, limit=1)

    if not rows:
        return {"hit": False, "reason": "cache_empty"}

    prompt, response, model_name, similarity = rows[0]

    if similarity < THRESHOLD:
        return {
            "hit": False,
            "reason": "below_threshold",
            "similarity": similarity,
            "nearest_prompt": prompt,
        }

    return {
        "hit": True,
        "similarity": similarity,
        "matched_prompt": prompt,
        "response": response,
        "model": model_name,
    }


@app.post("/store")
def store(req: StoreRequest):
    embedding = model.encode(req.prompt)
    insert_entry(conn, req.prompt, req.response, req.model, embedding)
    return {"stored": True}
