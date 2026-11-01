from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

PAIRS = [
    # --- Should hit: same question, different phrasing ---
    ("How do I reset my password?",
     "I forgot my password, how do I change it?", True),
    ("What are your business hours?",
     "When are you open?", True),
    ("How do I cancel my subscription?",
     "I want to cancel my plan, what do I do?", True),
    ("What is the capital of France?",
     "Which city is the capital of France?", True),

    # --- Must NOT hit: entity swapped ---
    ("What is the capital of France?",
     "What is the capital of Germany?", False),
    ("How do I reset my password?",
     "How do I reset my username?", False),

    # --- Must NOT hit: numbers changed ---
    ("What is 2 + 2?", "What is 2 + 3?", False),
    ("Convert 100 USD to INR", "Convert 200 USD to INR", False),

    # --- Must NOT hit: negated ---
    ("Is this medication safe during pregnancy?",
     "Is this medication unsafe during pregnancy?", False),
    ("Should I accept the offer?",
     "Should I reject the offer?", False),

    # --- Must NOT hit: personalised / stateful ---
    ("What is my account balance?",
     "What is my current balance?", False),
]

rows = []
for a, b, acceptable in PAIRS:
    ea, eb = model.encode([a, b])
    score = util.cos_sim(ea, eb).item()
    rows.append((score, acceptable, a, b))

rows.sort(reverse=True)

print(f"{'SCORE':<8} {'SHOULD HIT':<12} PAIR")
print("-" * 100)
for score, acceptable, a, b in rows:
    label = "YES" if acceptable else "NO  <-- DANGER" if score > 0.80 else "NO"
    print(f"{score:.4f}   {label:<12} {a[:40]:<42} | {b[:40]}")

safe = [s for s, ok, _, _ in rows if ok]
unsafe = [s for s, ok, _, _ in rows if not ok]

print("\n" + "=" * 100)
print(f"Pairs that SHOULD hit:     min={min(safe):.4f}  max={max(safe):.4f}")
print(f"Pairs that must NOT hit:   min={min(unsafe):.4f}  max={max(unsafe):.4f}")

if max(unsafe) > min(safe):
    print("\nThe two groups OVERLAP. No single threshold separates them cleanly.")
    print(f"Any threshold below {max(unsafe):.4f} serves at least one wrong answer.")
    print(f"Any threshold above {min(safe):.4f} misses at least one real opportunity.")