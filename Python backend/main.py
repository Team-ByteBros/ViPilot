from fastapi import FastAPI, UploadFile, File
import shutil
from resumeParse import extract_text, parse_resume
from roleMatch import recommend_roles

app = FastAPI()

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_path)
    resume_data = parse_resume(text)
    print(resume_data)
    roles = recommend_roles(text)

    return {
        "recommended_roles": roles
    }
