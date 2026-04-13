# 6-Phase GEO Audit Process

## Phase 1: Set the Foundation
*~30 minutes. Do this before touching any LLM.*

- Write the ICP in one sentence — role, company size, problem they're solving
- Name their top 3 competitors (the ones they actually lose deals to)
- Identify their product category — the phrase a buyer would use to search for what they do
- Note their content footprint — blog, comparison pages, G2/Capterra profile, review platforms
- List their use cases (check the website: /use-cases, /solutions, /platform)

Output: fill in Phase 1 section of `company-audit-template.md`

---

## Phase 2: Build the Prompt Set
*~30 minutes.*

Write 10–15 prompts their ICP would actually type into ChatGPT or Perplexity. Use buying language, not category jargon.

Organise into three groups:

**Category prompts** — "best [category] software for [use case]"
**Competitive prompts** — "alternatives to [competitor]", "[company] vs [competitor]"
**Problem prompts** — "how do I solve [specific pain point]" where a tool recommendation is a natural answer

Remove any prompt where naming a specific brand is NOT a natural response — those won't surface recommendations.

Output: 10–15 prompts saved in the audit folder

---

## Phase 3: Run the LLM Audit
*~1–2 hours.*

Run every prompt across:
- Perplexity (most transparent — shows citations)
- ChatGPT
- One of Claude or Gemini

For each response, record:
- Is the company mentioned? Yes / No
- Which competitors are mentioned?
- What position / framing does the company get (recommended, alternative, absent)?
- Which third-party URLs are cited?

Tally: visibility % for the company vs competitors across the full prompt set.

Flag the 2–3 most damaging gaps — prompts where a direct competitor dominates and the company is absent.

Output: completed `geo-audit.md`

---

## Phase 4: Diagnose Why the Gap Exists
*~30 minutes.*

- Check if the company appears on the third-party pages LLMs cited
- Check if those pages include accurate, current information
- Check whether AI crawlers are blocked (Cloudflare settings, robots.txt)
- Note whether their content structure supports LLM crawlability — comparison pages, FAQs, use case pages, or only generic blog posts

Output: gap diagnosis section of `geo-audit.md`

---

## Phase 5: Translate to Business Terms
*~30 minutes.*

Reframe in sales language, not SEO language:
- "When your buyer asks ChatGPT which platform to use, [Competitor X] is recommended. You are not mentioned."
- "That conversation is happening before your sales team gets on a call."
- "The trust gap exists before the first human interaction."

Identify the one prompt where the risk is highest — the one most likely to reflect a real pre-purchase moment.

Output: business translation section of `one-pager.md`

---

## Phase 6: Build the One-Pager
*~30 minutes.*

Structure as four blocks:

1. **Where you stand today** — visibility % in LLMs, vs top 3 competitors
2. **Where the gap hurts most** — 2–3 specific prompts where competitors dominate and company is absent
3. **Why the gap exists** — third-party presence, crawlability, content structure (brief, non-technical)
4. **What closing the gap involves** — third-party placements, own-site content, monitoring cadence

End with a decision frame, not a CTA:
*"If your buyers are consulting LLMs before they contact you — and the data suggests they are — this gap is costing you trust before your first sales call."*

Output: `one-pager.md`
