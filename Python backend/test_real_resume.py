from resumeParse import ResumeParser
from resumeScorer import ResumeScorer, JobDescriptionParser
import json

def test_real_resume():
    # 1. Initialize
    parser = ResumeParser()
    scorer = ResumeScorer()
    jd_parser = JobDescriptionParser()
    
    # 2. Parse Resume
    pdf_path = "temp_ResumeUpdated24Nov.pdf"
    print(f"Parsing {pdf_path}...")
    try:
        text = parser.extract_text(pdf_path)
        resume_data = parser.parse_text(text)
        print("Resume Parsed Successfully.")
        print(f"Name: {resume_data.get('name')}")
        print(f"Skills Found: {resume_data.get('skills')[:10]}...") # Show first 10
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return

    # 3. Define a Sample JD (Android Engineer)
    jd_text = """
    Job Title: Android Engineer
    
    Must Have:
    - Strong experience with Kotlin and Java.
    - Expertise in Jetpack Compose for UI development.
    - Experience with Firebase and Firestore.
    - Knowledge of MVVM architecture and Hilt for dependency injection.
    
    Good to Have:
    - Experience with Node.js or backend integration.
    - Familiarity with MongoDB or NoSQL databases.
    - Published apps on Play Store.
    """
    
    print("\nParsing Sample JD...")
    jd_data = jd_parser.parse(jd_text)
    print("Parsed JD Data:", json.dumps(jd_data, indent=2))
    
    # 4. Score
    print("\nScoring Resume against JD...")
    # Pass extracted sentences!
    resume_sentences = resume_data.get('sentences', [])
    score_result = scorer.score(resume_data['skills'], jd_data, resume_sentences)
    
    # 5. Output
    print("-" * 50)
    print(f"FINAL SCORE: {score_result['score']}")
    print(f"VERDICT: {score_result['verdict']}")
    print("-" * 50)
    
    print("\nMATCH DETAILS:")
    print(f"Exact Matches: {score_result['breakdown']['exact']}")
    print(f"Contextual Matches (+0.3 boost):")
    for m in score_result['breakdown']['contextual']:
        print(f"  - {m['skill']}: \"{m['evidence']}\"")
        
    print(f"Semantic/Textual Matches (+0.6 boost):")
    for m in score_result['breakdown']['semantic']:
        print(f"  - {m['skill']} (Conf: {m['confidence']:.2f}): \"{m['evidence']}\"")
        
    print(f"Missing Skills: {score_result['breakdown']['missing']}")

if __name__ == "__main__":
    test_real_resume()
