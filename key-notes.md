## Retrieval-miss threshold

When the user asks a question, the backend embeds it as a vector and searches Chroma for the most similar document chunks. Chroma returns a ranked list, each chunk with a similarity score (cosine similarity
by default — 0.0 = unrelated, 1.0 = identical text).

The retrieval-miss threshold is the floor: if the best returned chunk scores below it, we treat the query as "no relevant docs found" and short-circuit. We deliberately do NOT pass weak chunks to the LLM,
because the LLM would either hallucinate from thin context or confidently answer from off-topic material — both worse than admitting "I don't know."

Why a tunable env var (RETRIEVAL_MIN_SCORE=0.3) instead of a hard-coded constant:

- The "right" threshold depends on the actual corpus. A tight, well-curated set of ROCS manuals might cluster scores in the 0.5–0.8 range; a noisier mixed corpus might sit in 0.2–0.5. Hard-coding now would
  be guessing.
- Lets us A/B test in dev without code changes — bump the env var, restart Flask, re-test.
- 0.3 is a reasonable-ish starting default for OpenAI text-embedding-3-small on technical docs, but expect to retune after the first 10–20 real planner questions.

What happens when the threshold is missed (per Section 4 decision):

- Backend skips the LLM call entirely.
- Streams back a canned answer: "I don't have documentation that covers this. Try rephrasing or asking about a specific error code / module."
- No source event is emitted (there are no good sources to cite).

Trade-offs to revisit after real usage:

- Too high → bot says "I don't know" for questions it could have handled with mild context. Frustrating.
- Too low → bot answers from loosely related chunks and confabulates. Worse than admitting ignorance.
- Start at 0.3, watch what real users hit, adjust.
