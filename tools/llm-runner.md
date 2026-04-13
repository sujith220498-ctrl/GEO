# LLM Audit Runner

Instructions for running prompts and recording results.

---

## Tools to Use

**Perplexity** (primary — use this first)
- URL: perplexity.ai
- Why: Shows citations explicitly. You can see exactly which third-party URLs the model is pulling from.
- How: Run each prompt. Screenshot or copy the full response. Note every brand mentioned and every URL cited.

**ChatGPT** (secondary)
- Model: GPT-4o
- Why: Largest user base — most likely what your buyers are using.
- How: Run same prompts. Note whether web search is on or off (affects results significantly).

**Gemini** (tertiary)
- Why: Google-native — pulls from Google's index, different citation pattern from Perplexity.
- How: Run same prompts. Useful for catching gaps Perplexity misses.

---

## What to Record Per Prompt

For each prompt + LLM combination:

1. **Company mentioned?** Yes / No
2. **If yes:** What framing? (recommended, listed as alternative, mentioned once, cited as example)
3. **Competitors mentioned:** List all named brands
4. **Third-party URLs cited:** Copy every URL shown as a source
5. **Response quality:** Does the model give a confident recommendation or a generic/hedged answer?

---

## Recording Template (copy per prompt)

```
Prompt: [exact prompt text]
LLM: Perplexity / ChatGPT / Gemini
Date: YYYY-MM-DD

Company mentioned: Yes / No
Framing: [recommended / alternative / absent]
Competitors named: [list]
URLs cited:
  - [url 1]
  - [url 2]
  - [url 3]
Notes: [anything notable about tone, accuracy, or framing]
```

---

## Scoring

After running all prompts across all LLMs:

- **Visibility %** = (prompts where company is mentioned) / (total prompts) × 100
- **Position quality** = how often the company is the primary recommendation vs listed as an alternative
- **Citation overlap** = how many of the cited third-party URLs also feature the company

---

## Red Flags to Escalate

- Company is absent in a prompt that directly describes their product
- A competitor appears in every single prompt
- The model describes the company inaccurately (wrong use cases, wrong pricing, outdated info)
- The model confidently recommends a competitor with zero hedging
- No third-party URLs cited in the response — model is drawing from its own training data (older, harder to influence)
