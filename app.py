import json
import os

import streamlit as st
from groq import Groq
from pypdf import PdfReader

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL = "llama-3.3-70b-versatile"

st.set_page_config(page_title="AI Resume Matcher", page_icon="📄")
st.title("📄 AI Resume-to-Job Matcher")
st.caption("Upload your resume, paste a job description, and see how well they match.")


def get_api_key():
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.getenv("GROQ_API_KEY")


def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()


def analyze(resume_text, job_description, api_key):
    client = Groq(api_key=api_key)
    system = (
        "You are an expert recruiter and ATS specialist. Compare the resume to the "
        "job description. Respond ONLY with a JSON object with these keys: "
        '"score" (integer 0-100), "matched_skills" (list of strings), '
        '"missing_keywords" (list of strings), "suggestions" (list of exactly 3 '
        "specific, actionable strings)."
    )
    user = f"RESUME:\n{resume_text[:8000]}\n\nJOB DESCRIPTION:\n{job_description[:5000]}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


uploaded = st.file_uploader("Resume (PDF)", type=["pdf"])
job_desc = st.text_area("Job description", height=220)

if st.button("Analyze", type="primary"):
    api_key = get_api_key()
    if not api_key:
        st.error("API key not found. Set GROQ_API_KEY in .env or Streamlit secrets.")
    elif not uploaded or not job_desc.strip():
        st.warning("Please upload a resume and paste a job description.")
    else:
        resume_text = extract_text(uploaded)
        if len(resume_text) < 50:
            st.error("Couldn't read text from this PDF. It may be a scanned image.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    result = analyze(resume_text, job_desc, api_key)
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    st.stop()

            score = int(result.get("score", 0))
            st.subheader(f"Match score: {score}/100")
            st.progress(min(max(score, 0), 100) / 100)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Matched skills**")
                for s in result.get("matched_skills", []):
                    st.write(f"- {s}")
            with col2:
                st.markdown("**❌ Missing keywords**")
                for s in result.get("missing_keywords", []):
                    st.write(f"- {s}")

            st.markdown("**💡 How to improve**")
            for i, tip in enumerate(result.get("suggestions", []), 1):
                st.write(f"{i}. {tip}")
