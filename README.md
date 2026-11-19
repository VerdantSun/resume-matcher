# 📄 AI Resume-to-Job Matcher

Upload your resume (PDF), paste a job description, and get:
- a match score out of 100
- matched skills and missing keywords
- 3 specific tips to improve your resume for that role

**Live demo:** <paste your Streamlit link here>

![screenshot](screenshot.png)

## Tech stack
Python, Streamlit, pypdf, Groq API (Llama 3.3 70B)

## Run locally
```bash
git clone https://github.com/<your-username>/resume-matcher.git
cd resume-matcher
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
streamlit run app.py
```

## How it works
1. `pypdf` extracts text from the uploaded resume.
2. The resume and job description are sent to an LLM with a prompt that requests JSON output.
3. Streamlit renders the score, skills and suggestions.

## Limitations
Scanned (image-only) PDFs aren't supported. The score is an AI estimate, not a real ATS result.
