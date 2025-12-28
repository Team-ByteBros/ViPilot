from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from resumeParse import ResumeParser

app = FastAPI()

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    # Create temp file path
    file_path = f"temp_{file.filename}"

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Initialize parser and extract data
        parser = ResumeParser()
        data = parser.parse(file_path)
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
