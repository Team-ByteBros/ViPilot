from resumeScorer import ResumeScorer, JobDescriptionParser

def test_scoring():
    scorer = ResumeScorer()
    # Mock JD
    jd_data = {
        'must_have': ['Python', 'Kubernetes'],
        'good_to_have': ['React'],
        'all_keywords': ['Python', 'Kubernetes', 'React']
    }
    
    # Mock Resume
    resume_skills = ['Python', 'Django'] # Kubernetes missing from explicit skills, but maybe in text?
    resume_sentences = [
        "I have 5 years of experience with Python and Django.",
        "Deployed microservices on Kubernetes using Helm charts.", # Semantic/Contextual potential
        "Built responsive UI.", # React missing
    ]
    
    print("\n--- Running Score Test ---")
    result = scorer.score(resume_skills, jd_data, resume_sentences)
    
    print(f"Score: {result['score']}")
    print(f"Verdict: {result['verdict']}")
    print("\nBreakdown:")
    print(f"Exact Matches: {result['breakdown']['exact']}")
    print(f"Contextual Matches: {result['breakdown']['contextual']}")
    print(f"Semantic Matches: {result['breakdown']['semantic']}")
    print(f"Missing: {result['breakdown']['missing']}")
    
    # Assertions
    # Python should be Exact match
    assert 'python' in result['breakdown']['exact']
    
    # Kubernetes should be Semantic match (it's in sentences, not skills list, and "Deployed" is an action verb but k8s is the noun)
    # "Deployed microservices on Kubernetes" -> Kubernetes skill. 
    # Wait, semantic match checks MISSING skills against sentences.
    # Kubernetes is missing from resume_skills.
    # It should match "Deployed microservices on Kubernetes..." via semantic similarity.
    
    found_k8s = False
    for item in result['breakdown']['semantic']:
        if item['skill'] == 'kubernetes':
            found_k8s = True
            print(f"\n[SUCCESS] Semantic match found for Kubernetes: {item['evidence']} (Conf: {item['confidence']:.2f})")
    
    if not found_k8s:
        print("\n[FAIL] Kubernetes semantic match NOT found (check model/threshold).")
        
    # Check contextual
    # 'python' is in skills. sentence: "experience with Python..." -> no action verb
    # If we add "Developed backend using Python", it should trigger contextual.
    
    print("\n--- Contextual Test ---")
    result_ctx = scorer.score(['python'], jd_data, ["Developed backend using Python"])
    # Should have higher score or be marked contextual
    ctx_match = result_ctx['breakdown']['contextual']
    if ctx_match:
         print(f"[SUCCESS] Contextual match detected for Python: {ctx_match}")
    else:
         print("[WARNING] Contextual match NOT detected for Python.")

if __name__ == "__main__":
    test_scoring()
