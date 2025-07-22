

import os
import fitz  # PyMuPDF
import gradio as gr
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Sample corpus for training Word2Vec
corpus = [
    "experienced data scientist with knowledge in python machine learning pandas",
    "machine learning engineer skilled in tensorflow keras deep learning models",
    "looking for a machine learning expert with strong python skills and neural network experience",
    "ai specialist with experience in deep learning pytorch and computer vision",
    "data analyst proficient in SQL Excel and data visualization with Tableau",
]
tokenized_corpus = [doc.lower().split() for doc in corpus]

# Train Word2Vec model
model = Word2Vec(sentences=tokenized_corpus, vector_size=100, window=2, min_count=1, sg=1, seed=42)

# Vectorize a document
def document_vector(doc):
    words = doc.lower().split()
    word_vecs = [model.wv[word] for word in words if word in model.wv]
    return np.mean(word_vecs, axis=0) if word_vecs else np.zeros(model.vector_size)

# Resume loader (PDF or TXT)
def load_resume(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".pdf":
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text

    else:
        raise ValueError("Unsupported file format. Please upload a .txt or .pdf file.")

# Matcher function
def match_resume(resume_file, job_description):
    try:
        resume_text = load_resume(resume_file)
        resume_vec = document_vector(resume_text)
        job_vec = document_vector(job_description)
        score = cosine_similarity([job_vec], [resume_vec])[0][0]
        match_score = round(score * 100, 2)

        if score > 0.75:
            verdict = "✅ Strong match: You are a great fit for this job!"
        elif score > 0.5:
            verdict = "🟡 Moderate match: You meet some of the job requirements."
        else:
            verdict = "❌ Weak match: Your resume may not align well with the job description."

        return f"📄 Resume Match Score: {match_score}%

{verdict}"

    except Exception as e:
        return f"❗ Error processing file: {str(e)}"

# Launch Gradio interface
interface = gr.Interface(
    fn=match_resume,
    inputs=[
        gr.File(label="Upload Resume (.txt or .pdf)", file_types=[".pdf", ".txt"]),
        gr.Textbox(lines=6, label="Paste Job Description"),
    ],
    outputs="text",
    title="📑 Resume vs Job Description Matcher",
    description="Upload your resume and paste a job description. The AI model will tell you how well you match!"
)

interface.launch(debug=True)

