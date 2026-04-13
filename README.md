# GEO Audit Repo

One GEO audit per company, per day.

## What This Repo Does

Maps where a B2B SaaS or AI company stands in organic search and LLM-generated recommendations — and what it would take to close the gap.

## Core Mental Model

You are not marketing to buyers. You are building the evidence base that an LLM uses to form a verdict about a company — before the buyer ever picks up the phone.

LLMs don't search. They synthesise. 97%+ of AI citations come from third-party domains the model already trusts — not from the company's own website. The question is not "how do I rank in ChatGPT?" It's "what evidence environment am I building for the model to draw from?"

---

## Repo Structure

```
geo-audit/
├── README.md                        — this file
├── DAILY-LOG.md                     — one line per audit, links to folder
├── framework/
│   ├── mental-model.md              — evidence architecture theory
│   ├── audit-process.md             — 6-phase audit process
│   └── prompt-templates.md          — prompt set templates by category
├── templates/
│   └── company-audit-template.md   — blank template for each new audit
├── tools/
│   ├── dataforseo_audit.py          — DataForSEO API script
│   └── llm-runner.md                — instructions for running LLM prompts
└── audits/
    └── [company-name]/
        └── [YYYY-MM-DD]/
            ├── seo-benchmark.md
            ├── geo-audit.md
            └── one-pager.md
```

---

## How to Run One Audit Per Day

**Step 1 — Create the company folder**
```
mkdir -p audits/[company-name]/[YYYY-MM-DD]
```

**Step 2 — Run SEO benchmark**
```
python tools/dataforseo_audit.py --domain example.com --markets "United States,India"
```

**Step 3 — Build the prompt set**
Open `framework/prompt-templates.md`. Write 10 prompts using the company's use cases, competitors, and buyer language.

**Step 4 — Run LLM audit**
Run each prompt on Perplexity, ChatGPT, Gemini. Record results in `geo-audit.md`.

**Step 5 — Write one-pager**
Use `templates/company-audit-template.md`. Facts only. No selling language.

**Step 6 — Log it**
Add one line to `DAILY-LOG.md`.

---

## Credentials

Store in a `.env` file — never commit to the repo:
```
DATAFORSEO_USERNAME=your-login
DATAFORSEO_PASSWORD=your-password
```

---

## Completed Audits

| Date | Company | Domain | One-Pager |
|---|---|---|---|
| 2026-04-13 | WorkOnGrid | workongrid.com | [View](audits/workongrid/2026-04-13/one-pager.md) |
