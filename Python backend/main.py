from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
from resumeParse import ResumeParser
from roleMatch import recommend_roles
from resumeScorer import JobDescriptionParser, ResumeScorer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

parser = ResumeParser()
jd_parser = JobDescriptionParser()
scorer = ResumeScorer()

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = parser.extract_text(file_path)
    resume_data = parser.parse_text(text)
    print(resume_data)
    roles = recommend_roles(text)

    return {
        "recommended_roles": roles
    }

@app.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...), job_description: str = Form(None)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_data = parser.parse(file_path)
    
    score_result = None
    if job_description:
        jd_data = jd_parser.parse(job_description)
        score_result = scorer.score(resume_data['skills'], jd_data, resume_sentences=resume_data.get('sentences', []))

    return {"resume_data": resume_data, "score_result": score_result}

@app.post("/score-resume")
async def score_resume_endpoint(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    # 1. Save and parse resume
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    resume_data = parser.parse(file_path)
    
    # 2. Parse Job Description
    jd_data = jd_parser.parse(job_description)
    
    # 3. Score
    score_result = scorer.score(resume_data['skills'], jd_data, resume_sentences=resume_data.get('sentences', []))
    
    return {
        "score_details": score_result,
        "resume_data": resume_data
    }
