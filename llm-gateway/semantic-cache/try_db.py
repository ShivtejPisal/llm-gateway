from sentence_transformers import SentenceTransformer
from db import connect, insert_entry, find_nearest

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = connect()

seed = [
    ("How do I reset my password?", "Click 'Forgot password' on the login page."),
    ("What are your business hours?", "We are open 9am to 6pm, Monday to Friday."),
    ("What is the capital of France?", "Paris."),
]

for prompt, response in seed:
    insert_entry(conn, prompt, response, "seed", model.encode(prompt))
print(f"Inserted {len(seed)} entries\n")

queries = [
    "I forgot my password, how do I change it?",
    "When are you open?",
    "What is the capital of Germany?",
]

for q in queries:
    rows = find_nearest(conn, model.encode(q), limit=1)
    prompt, response, _, similarity = rows[0]
    print(f"Query:   {q}")
    print(f"Nearest: {prompt}")
    print(f"Score:   {similarity:.4f}")
    print(f"Answer:  {response}\n")

conn.close()