# 🎯 HireSense — AI Resume Screening System

An AI-powered resume screener built with **Streamlit** and **Google Gemini 2.5 Flash Lite** .  
Upload multiple candidate PDFs, paste a Job Description, and get instant ranked results with scores, strengths, gaps, and recommendations.

---

## 📸 Features

- 📄 Upload multiple PDF resumes at once
- 🧠 Semantic matching using `sentence-transformers` (all-MiniLM-L6-v2)
- 📊 Match score (0–100) via cosine similarity
- ✨ AI-generated strengths, gaps & recommendation via **Gemini 2.5 Flash Lite** 
- 🏆 Candidate ranking (highest to lowest)
- ⬇️ Download results as CSV
- 🔑 API key stored safely in `.env` — never exposed on GitHub

---

## 🗂️ Project Structure

```
resume_screener/
│
├── app.py                  ← Entry point (streamlit run app.py)
├── requirements.txt        ← Python dependencies
├── .env.example            ← API key template (safe to commit)
├── .env                    ← Your real key (git ignored)
├── .gitignore
├── setup.bat               ← One-click setup for Windows
├── setup.sh                ← One-click setup for Mac/Linux
│
└── modules/
    ├── __init__.py
    ├── config.py           ← Loads .env, exposes GOOGLE_API_KEY
    ├── ui.py               ← App orchestrator
    ├── components.py       ← Reusable Streamlit UI widgets
    ├── styles.py           ← All custom CSS
    ├── pdf_extractor.py    ← PDF → plain text (PyPDF2)
    ├── scorer.py           ← Embeddings, cosine similarity, ranking
    ├── insights.py         ← Gemini AI strengths/gaps + keyword fallback
    └── exporter.py         ← CSV export builder
```

---

## ⚙️ Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Similarity | `scikit-learn` cosine similarity |
| PDF parsing | PyPDF2 |
| LLM  | Google Gemini 2.5 Flash Lite |
| Config | `python-dotenv` |

---

## 🚀 Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/your-username/resume-screener.git
cd resume-screener
```

### 2. Create virtual environment & install

**Windows:**
```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your Gemini API key

```bash
cp .env.example .env
```

Open `.env` and add your key:
```
GOOGLE_API_KEY=AIza-your-key-here
```

> **Get a  key** (no credit card needed) at 👉 [aistudio.google.com](https://aistudio.google.com) → click **Get API key**

### 4. Run the app

**Windows:**
```bat
venv\Scripts\activate
streamlit run app.py
```

**Mac / Linux:**
```bash
source venv/bin/activate
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## 🧠 How It Works

```
PDF Resumes  ──► Extract Text (PyPDF2)
                      │
                      ▼
Job Description ──► Sentence Embeddings (all-MiniLM-L6-v2)
                      │
                      ▼
              Cosine Similarity Score (0–100)
                      │
                      ▼
           Gemini 2.5 Flash Lite ()
           → Strengths, Gaps, Recommendation
                      │
                      ▼
              Ranked Results + CSV Export
```

**Scoring tiers:**
| Score | Recommendation |
|---|---|
| ≥ 70 | ✅ Strong Fit |
| 50–69 | 🟡 Moderate Fit |
| < 50 | ❌ Not Fit |

---

## 🔒 API Key Safety

- Real key lives only in `.env` — **never committed to GitHub**
- `.env` is listed in `.gitignore`
- `.env.example` (with placeholder values) is what gets committed
- No key is ever entered in the UI or hardcoded anywhere in the code

---

## 📦 Dependencies

```
streamlit
sentence-transformers
scikit-learn
PyPDF2
numpy
python-dotenv
google-generativeai
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 📤 Output Example

| Rank | Candidate | Score | Recommendation | Strengths | Gaps |
|---|---|---|---|---|---|
| 1 | John Doe | 84 | ✅ Strong Fit | Strong Python, SQL | Weak cloud experience |
| 2 | Jane Smith | 67 | 🟡 Moderate Fit | Good ML background | No leadership experience |
| 3 | Bob Ray | 41 | ❌ Not Fit | Basic Excel skills | Missing core tech stack |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## 📄 License

MIT