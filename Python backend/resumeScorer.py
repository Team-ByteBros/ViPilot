import re
from typing import List, Dict, Set, Tuple

class JobDescriptionParser:
    """Parses job descriptions to extract skill requirements."""
    
    def __init__(self):
        # Patterns for different skill categories
        self.sections_patterns = {
            'must_have': [
                r'must\s*have', r'required\s*skills?', r'requirements', r'qualifications', 
                r'essential', r'minimum\s*qualifications', r'what\s*you\s*need'
            ],
            'good_to_have': [
                r'good\s*to\s*have', r'nice\s*to\s*have', r'preferred', r'desired', 
                r'plus', r'bonus', r'additional\s*skills?'
            ]
        }
    
    def parse(self, text: str) -> Dict[str, List[str]]:
        """
        Parses the JD text and segments it into Must Have vs Good to Have.
        Returns extracted keywords for each category.
        """
        # Pre-process: Insert newlines before headers to handle inline headers
        # e.g. "Skills: Java. Education: B.Tech" -> "Skills: Java.\nEducation: B.Tech"
        for section, patterns in self.sections_patterns.items():
            for pattern in patterns:
                # Look for pattern preceded by punctuation/space and followed by colon/space
                # We add \n before it.
                text = re.sub(r'([\.\?!]|\b)\s*(' + pattern + r')[:\s]', r'\n\2:', text, flags=re.IGNORECASE)
        
        lines = text.split('\n')
        
        parsed_data = {
            'must_have': [],
            'good_to_have': [],
            'all_keywords': []
        }
        
        current_section = 'must_have' # Default
        
        for line in lines:
            line_clean = line.strip() # maintain case for now
            if not line_clean:
                continue
            
            line_lower = line_clean.lower()
                
            # Check if line starts with a header
            is_header = False
            for section, patterns in self.sections_patterns.items():
                for pattern in patterns:
                    # Check if line *starts* with pattern
                    match = re.match(r'^\s*(' + pattern + r')[:\s]*(.*)', line_lower)
                    if match:
                        current_section = section
                        is_header = True
                        
                        # Process content after header immediately
                        content = match.group(2).strip()
                        if content:
                            self._extract_keywords(content, current_section, parsed_data)
                        break
                if is_header:
                    break
            
            if is_header:
                continue
            
            # Regular line (continuation of previous section)
            self._extract_keywords(line_clean, current_section, parsed_data)
                    
        return parsed_data

    def _extract_keywords(self, text, section, parsed_data):
        # Split by commas, bullets, etc.
        parts = re.split(r'[,•·:\-\/]', text)
        for part in parts:
            cleaned = part.strip()
            # Clean up trailing punctuation
            cleaned = re.sub(r'[\.\?!]+$', '', cleaned)
            
            if 1 < len(cleaned) < 30: 
                if section == 'must_have':
                    parsed_data['must_have'].append(cleaned)
                else:
                    parsed_data['good_to_have'].append(cleaned)
                parsed_data['all_keywords'].append(cleaned)
                    
        return parsed_data

class ResumeScorer:
    """Scores a resume against JD requirements."""
    
    def __init__(self):
        self.weights = {
            'must_have': 10,
            'good_to_have': 5,
            'keyword_match': 1
        }
    
    def normalize_skill(self, skill: str) -> str:
        return skill.strip().lower()
    
    def extract_skills_from_jd(self, jd_text_list: List[str]) -> Set[str]:
        """
        Refines the raw lines from JD parser into a set of distinct normalized skills.
        In a real app, this would use the same entity extraction as the resume parser.
        For now, we assume the JD parser produces relatively clean list items.
        """
        skills = set()
        for item in jd_text_list:
             # Basic cleanup: remove common stopwords if necessary
             # For now, just add the item as a normalized string
             skills.add(self.normalize_skill(item))
        return skills

    def score(self, resume_skills: List[str], jd_data: Dict[str, List[str]]) -> Dict:
        """
        Calculates the relevance score.
        """
        resume_skills_set = {self.normalize_skill(s) for s in resume_skills}
        
        # Refine JD skills (simple normalization for matching)
        must_have_skills = self.extract_skills_from_jd(jd_data['must_have'])
        good_to_have_skills = self.extract_skills_from_jd(jd_data['good_to_have'])
        
        # Calculate matches
        matched_must_have = must_have_skills.intersection(resume_skills_set)
        matched_good_to_have = good_to_have_skills.intersection(resume_skills_set)
        
        missing_must_have = must_have_skills - matched_must_have
        missing_good_to_have = good_to_have_skills - matched_good_to_have
        
        # Calculate Score
        # Max score is if all JD must-have and good-to-have are matched
        total_possible = (len(must_have_skills) * self.weights['must_have']) + \
                         (len(good_to_have_skills) * self.weights['good_to_have'])
        
        if total_possible == 0:
            # Fallback if no specific sections found, treat all keywords as finding match
             # (This handles JDs that are just a blob of text)
            total_possible = 100 # arbitrary base
            current_score = 0
            # Try to match any resume skill against strict keyword list? 
            # Let's keep it 0 if JD is empty to warn user.
            final_score = 0
        else:
            current_score = (len(matched_must_have) * self.weights['must_have']) + \
                            (len(matched_good_to_have) * self.weights['good_to_have'])
            final_score = (current_score / total_possible) * 100
        
        return {
            "score": round(final_score, 2),
            "breakdown": {
                "must_have_matched": list(matched_must_have),
                "must_have_missing": list(missing_must_have),
                "good_to_have_matched": list(matched_good_to_have),
                "good_to_have_missing": list(missing_good_to_have)
            },
           "details": {
               "total_must_have": len(must_have_skills),
               "total_good_to_have": len(good_to_have_skills)
           }
        }
