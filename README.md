# ReqLens

Turn messy engineering notes into clean, reviewed requirements — powered by Gemini, built for engineers who care about quality.

---

## The Problem

Meeting notes, spec emails, and review threads are full of requirements buried in paragraphs. Extracting them manually is slow, inconsistent, and easy to get wrong.

## The Solution

Paste your raw text. ReqLens calls Gemini, extracts structured requirements, and hands them back to you in an editable table — typed, prioritized, and ready for review. You stay in control of every decision.

---

## How It Works

**1. Extract** — paste any engineering text or upload a `.txt` file. Gemini returns structured requirements with type, priority, and source phrase.

**2. Review** — edit the table directly. Change types, adjust priorities, mark rows as Accepted. Built-in validation catches empty rows and duplicates before you export.

**3. Export** — download as CSV or save a snapshot to session history.

---

## Under the Hood

A few decisions worth noting for anyone reading the code:

- **Structured JSON output** via `response_mime_type="application/json"` — no regex, no fragile parsing.
- **Result dict pattern** — `extract()` never raises. It always returns `{ok, records, error}` so the UI stays in control.
- **Typed schema** — `RequirementRecord` dataclass keeps the data contract explicit throughout.
- **Normalized duplicate detection** — text is lowercased and whitespace-collapsed before comparison.
- **Immutable history snapshots** — `df.copy()` on save, so editing the current table never corrupts past snapshots.

---

## Stack

Python · Streamlit · Google Gemini 2.5 Flash · pandas

---

## Run Locally

```bash
git clone https://github.com/ahmedgeeter/ReqLens.git
cd ReqLens
pip install -r requirements.txt
```

Add your Gemini API key (free at [aistudio.google.com](https://aistudio.google.com)):

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your-key-here"
```

```bash
streamlit run streamlit_app.py
```

No key yet? Load `data/sample_input.txt` from the Extract page to see the full workflow.

---

## Project Layout

```
core/
  gemini.py       Gemini integration + error handling
  schema.py       RequirementRecord dataclass
  validators.py   Validation rules + duplicate detection
  export.py       CSV export
pages/
  1_Extract.py    Main workflow
  2_History.py    Session snapshot browser
```

---

> Built as a focused, realistic tool — not a demo. Every design decision has a reason.
