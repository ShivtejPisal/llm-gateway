"""
Phase 3 spike: understand what embeddings are and how similarity behaves.
Run:  python explore.py
"""
import time
from sentence_transformers import SentenceTransformer, util

print("Loading model (first run downloads ~90MB)...")
start = time.time()
model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Model loaded in {time.time() - start:.1f}s\n")

sentences = [
    "How do I reset my password?",
    "I forgot my login details, how can I change them?",
    "What is the capital of France?",
    "What is the best pizza in Naples?",
]

start = time.time()
embeddings = model.encode(sentences)
elapsed_ms = (time.time() - start) * 1000

print(f"Encoded {len(sentences)} sentences in {elapsed_ms:.1f}ms")
print(f"Shape: {embeddings.shape}")
print(f"First 8 numbers of sentence 0:\n{embeddings[0][:8]}\n")

print("Pairwise cosine similarity:")
print("-" * 70)
for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        score = util.cos_sim(embeddings[i], embeddings[j]).item()
        print(f"{score:.4f}  |  {sentences[i][:32]:<34} <-> {sentences[j][:32]}")