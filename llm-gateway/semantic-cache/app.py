from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

class EmbedRequest(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok", "dimensions": 384}

@app.post("/embed")
def embed(req: EmbedRequest):
    vector = model.encode(req.text)
    return {"vector": vector.tolist(), "dimensions": len(vector)}