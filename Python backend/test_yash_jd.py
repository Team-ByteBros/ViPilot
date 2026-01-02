import sys
import os
import json

# Add current dir to path
sys.path.append(os.getcwd())

from resumeParse import ResumeParser
from resumeScorer import JobDescriptionParser, ResumeScorer

def test_yash():
    print("Initializing parsers...")
    resume_parser = ResumeParser()
    jd_parser = JobDescriptionParser()
    scorer = ResumeScorer()
    
    # 1. Load Resume
    resume_path = "YashResume.pdf"
    if not os.path.exists(resume_path):
        print(f"Error: {resume_path} not found.")
        return

    print(f"Processing {resume_path}...")
    try:
        resume_text = resume_parser.extract_text(resume_path)
        resume_data = resume_parser.parse_text(resume_text)
        print("Resume parsed successfully.")
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return

    # 2. Define JD
    jd_text = """
    About the Role - We are looking for motivated and enthusiastic Engineering Interns to join our dynamic team. This internship provides an excellent opportunity to gain real-world experience in designing, developing, and enhancing enterprise software solutions used across global supply chains. www.TraceLink.com © 2025 TraceLink, Inc. All rights reserved.Key Responsibilities • • • • • • Assist in the design, development, and testing of software features across Tracelink’s platform. Collaborate with senior engineers to troubleshoot, debug, and resolve technical issues. Participate in code reviews, sprint planning, and daily standups as part of an agile environment. Write clean, maintainable, and efficient code following best practices. Support integration, QA, and DevOps teams with required technical tasks. Contribute to documentation, test cases, and automation efforts. Qualifications: • • • • • • Pursuing a Bachelor’s or master’s degree in computer science, IT, or related engineering fields. Strong understanding of programming fundamentals (Java, Python, JavaScript, or similar). Basic knowledge of data structures, algorithms, and OOP concepts. Familiarity with web technologies, databases, or cloud concepts is a plus. Good analytical and problem-solving skills. Strong communication skills and eagerness to learn. Preferred Skills (Good to Have) • • • • • Exposure to frameworks such as Spring Boot, React, or Node.js. Understanding of REST APIs and microservices architecture. Knowledge of version control systems like Git. Experience with SQL/NoSQL databases. Familiarity with CI/CD pipelines or DevOps concepts What You’ll Gain • • • • Hands-on experience working with a global product engineering team. Mentorship from experienced engineers and leaders. A collaborative and growth-focused environment. Opportunity to work on real, production-impacting projects.
    """

    # 3. Parse JD
    print("Parsing Job Description...")
    jd_data = jd_parser.parse(jd_text)
    
    # 4. Score
    print("Calculating Score...")
    score_result = scorer.score(
        resume_skills=resume_data['skills'],
        jd_data=jd_data,
        resume_sentences=resume_data.get('sentences', [])
    )
    
    # 5. Output
    print("\n" + "="*50)
    print(f"FINAL SCORE: {score_result['score']}%")
    print(f"VERDICT: {score_result['verdict']}")
    print("="*50)
    
    print("\nBreakdown:")
    print(f"Exact Matches: {score_result['breakdown']['exact']}")
    print(f"Semantic Matches: {[m['skill'] for m in score_result['breakdown']['semantic']]}")
    print(f"Missing Skills: {score_result['breakdown']['missing']}")
    
    print("\nDetails:")
    print(json.dumps(score_result, indent=2))

if __name__ == "__main__":
    test_yash()
