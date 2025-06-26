from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
import pdfplumber
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


app.mount("/", StaticFiles(directory="static", html=True), name="static")


def extract_text_from_pdf(file: UploadFile) -> str:
    with pdfplumber.open(file.file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text.strip()


def basic_cv_summary(text: str) -> str:
    
    lines = text.splitlines()
    non_empty = [l for l in lines if l.strip()]
    first_5 = "\n".join(non_empty[:5])
    return f"Extracted info:\n{first_5}"


async def summarize_with_openai(text: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Summarize the resume and list 3 selling points."},
                {"role": "user", "content": text}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"OpenAI error: {str(e)}"


@app.post("/process/", response_class=PlainTextResponse)
async def process_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return "Only PDF files are supported."

    text = extract_text_from_pdf(file)
    summary = basic_cv_summary(text)

    
    if openai.api_key:
        ai_summary = await summarize_with_openai(text)
        return f"{summary}\n\n---\n\n{ai_summary}"

    return summary