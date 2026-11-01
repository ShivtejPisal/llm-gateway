# Phase 3 Findings — Embedding Behaviour and Threshold Risk

**Model:** `all-MiniLM-L6-v2` (sentence-transformers)
**Vector dimensions:** 384
**Encode latency:** ~33ms for 4 sentences on CPU, after a 1.8s model load
**Date:** 2026-11-01

## Method

11 hand-labelled prompt pairs, each tagged with whether reusing one
prompt's cached answer for the other would be acceptable. Pairs were
chosen adversarially: four legitimate paraphrases and seven designed to
expose failure modes (entity swap, number change, negation, personalised
state).

## Headline result

| Group | Min | Max |
|---|---|---|
| Should hit (4 pairs) | 0.5083 | 0.9416 |
| Must NOT hit (7 pairs) | 0.6632 | 0.9778 |

**The ranges overlap almost completely.** The unsafe group's maximum
exceeds the safe group's maximum. No cosine-similarity threshold
separates them.

The highest-scoring pair in the whole set is the most dangerous one.

## Worst false positives

| Score | Pair | Failure mode |
|---|---|---|
| 0.9778 | "Is this medication safe during pregnancy" vs "...unsafe during pregnancy" | Negation |
| 0.9179 | "Convert 100 USD to INR" vs "Convert 200 USD to INR" | Number substitution |
| 0.8875 | "What is 2 + 2?" vs "What is 2 + 3?" | Number substitution |
| 0.8836 | "Should I accept the offer?" vs "Should I reject the offer?" | Antonym |
| 0.8324 | "What is my account balance?" vs "What is my current balance?" | Personalised / stateful |

### Negation is the dominant risk

Two characters ("un") invert the meaning of the medication question and
move the vector almost not at all. Embedding models are weak at negation
because negated and non-negated forms appear in near-identical contexts
during training. In a health or finance domain this failure mode alone
is disqualifying for an unguarded semantic cache.

### Numbers are near-invisible to the model

"100 USD" and "200 USD" scored 0.9179. The model encodes that both are
currency-conversion requests; the specific quantity barely registers.
Any workload involving calculation, amounts, dates or IDs is at risk.

## Missed opportunities (false negatives)

| Score | Pair |
|---|---|
| 0.5083 | "What are your business hours?" vs "When are you open?" |
| 0.6075 | "How do I cancel my subscription?" vs "I want to cancel my plan, what do I do?" |

These are unambiguous paraphrases that any threshold safe enough to
block the pairs above would reject. Both share intent but little
vocabulary or sentence structure.

## The underlying pattern

The model appears to weight **surface and structural similarity** more
heavily than **semantic intent**:

- Same sentence template + one word changed → high score, even when the
  answer differs completely.
- Different template + different vocabulary → low score, even when the
  answer is identical.

Supporting evidence from `explore.py`: "What is the capital of France?"
and "What is the best pizza in Naples?" — entirely unrelated questions —
scored 0.3202, far above the ~0.03 scored by pairs that differ in both
structure and topic. Shared question shape alone contributes measurable
similarity.

## Threshold tradeoff on this dataset

| Threshold | True hits | False hits | Precision |
|---|---|---|---|
| 0.95 | 0 | 1 | 0% |
| 0.94 | 1 | 1 | 50% |
| 0.89 | 2 | 2 | 50% |
| 0.85 | 2 | 4 | 33% |
| 0.60 | 3 | 7 | 30% |
| 0.50 | 4 | 7 | 36% |

**Important caveat:** this dataset is deliberately adversarial. Over half
the pairs were constructed specifically to break the model, which is not
representative of real traffic. These precision figures are a worst-case
stress test, not a prediction of production performance. Phase 5 needs a
dataset with a realistic ratio of easy to hard cases before any threshold
is chosen.

## Implications for Phase 4/5

1. A similarity threshold alone is **not** a sufficient safety mechanism.
2. The Phase 5 eval set must be realistically distributed, not
   adversarially stacked, or the measured precision will be meaningless.
3. Hard negatives must still be represented, or the eval will be too easy
   and the chosen threshold will be unsafe in production.
4. The cost of a false hit is not symmetrical with the cost of a miss. A
   miss costs one API call. A false hit returns a confidently wrong
   answer to a user. Threshold selection must reflect that asymmetry
   rather than optimising a balanced metric like accuracy or F1.

## Hypotheses to test later (not yet validated)

- A guard that blocks caching when prompts differ in any numeric token.
- A negation detector that forces a miss when one prompt contains a
  negation the other does not.
- A category blocklist: never semantically cache personalised or
  stateful prompts ("my account", "my order").
- A larger or instruction-tuned embedding model may separate these groups
  better — worth benchmarking against the same dataset.

TODO: my initial threshold instinct, and what I expect it to cost
TODO: 10 additional pairs from a domain I would actually build this for