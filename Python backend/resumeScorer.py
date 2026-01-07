import re
from typing import List, Dict, Set, Tuple
import torch
from sentence_transformers import SentenceTransformer, util
from model_utils import ModelManager

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
        # Use ResumeParser's known skills/extraction logic
        from resumeParse import ResumeParser
        self.skill_extractor = ResumeParser()
    
    def parse(self, text: str) -> Dict[str, List[str]]:
        """
        Parses the JD text and segments it into Must Have vs Good to Have.
        Returns extracted keywords for each category.
        """
        # Pre-process: Insert newlines before headers
        for section, patterns in self.sections_patterns.items():
            for pattern in patterns:
                text = re.sub(r'([\.\?!]|\b)\s*(' + pattern + r')[:\s]', r'\n\2:', text, flags=re.IGNORECASE)
        
        lines = text.split('\n')
        
        parsed_data = {
            'must_have': [],
            'good_to_have': [],
            'all_keywords': []
        }
        
        current_section = 'must_have' # Default
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            
            line_lower = line_clean.lower()
            
            # Check for Header
            is_header = False
            for section, patterns in self.sections_patterns.items():
                for pattern in patterns:
                     if re.match(r'^\s*(' + pattern + r')[:\s]*(.*)', line_lower):
                        current_section = section
                        is_header = True
                        content = re.match(r'^\s*(' + pattern + r')[:\s]*(.*)', line_lower).group(2).strip()
                        if content:
                            self._extract_keywords(content, current_section, parsed_data)
                        break
                if is_header: break
            
            if is_header:
                continue
            
            self._extract_keywords(line_clean, current_section, parsed_data)
                    
        return parsed_data

    def _extract_keywords(self, text, section, parsed_data):
        # Use ResumeParser's logic to extract technical skills from the line
        # We pass the text as a "skill line"
        extracted_skills = self.skill_extractor.extract_skills([text], [], "")
        
        for skill in extracted_skills:
            if skill not in parsed_data[section]:
                parsed_data[section].append(skill)
            if skill not in parsed_data['all_keywords']:
                parsed_data['all_keywords'].append(skill)
                    
        return parsed_data

class ResumeScorer:
    """Scores a resume against JD requirements."""
    
    def __init__(self):
        self.weights = {
            'must_have': 1,      # Base weight (modified by boosts)
            'good_to_have': 0.5,
            'keyword_match': 0.1
        }
        # Phase 2: Action Verbs
        self.ACTION_VERBS = {
            "build", "develop", "design", "implement",
            "optimize", "deploy", "scale", "integrate",
            "maintain", "architect", "create", "manage",
            "lead", "engineer", "test", "debug"
        }
        # Phase 3: Semantic Model
        # Load model only once using ModelManager
        self.model = ModelManager().get_model()
    
    def normalize_skill(self, skill: str) -> str:
        return skill.strip().lower()

    def is_contextual(self, skill: str, sentences: List[str]) -> Dict:
        """
        Check if a skill is used in a sentence with an action verb.
        """
        skill_norm = self.normalize_skill(skill)
        
        for sentence in sentences:
            if not sentence: continue
            words = sentence.lower().split()
            
            # Simple check if skill is in sentence
            if skill_norm in sentence.lower():
                # Check for action verbs in window
                # Find index of skill (approximate)
                try:
                    # simplistic word match - better to find index of skill start
                    # This is a heuristic.
                     if any(v in sentence.lower() for v in self.ACTION_VERBS):
                         return {"contextual": True, "evidence": sentence.strip()}
                except:
                    continue
                    
        return {"contextual": False, "evidence": None}

    def find_semantic_match(self, missing_jd_skill: str, resume_sentences: List[str], cached_sentence_embeddings=None) -> Dict:
        """
        Use embeddings to find if a missing skill is implicitly present.
        """
        if not self.model or not resume_sentences:
            return {"match": False, "confidence": 0, "evidence": None}
            
        skill_norm = self.normalize_skill(missing_jd_skill)

        # 1. First check if the skill is literally mentioned in any sentence (Textual Recovery)
        # This is faster and more accurate for explicit mentions.
        for sentence in resume_sentences:
            if not sentence: continue
            # Basic word boundary check could be better, but simple substring is a good start
            # or use regex for word boundary
            if skill_norm in sentence.lower():
                 return {
                    "match": True,
                    "confidence": 1.0, # High confidence for explicit mention
                    "evidence": sentence.strip()
                }

        try:
            # 2. Semantic Embedding Check
            # Encode missing skill
            jd_embedding = self.model.encode(missing_jd_skill, convert_to_tensor=True)
            
            # Encode sentences (batch) or use cached
            if cached_sentence_embeddings is not None:
                sentence_embeddings = cached_sentence_embeddings
            else:
                sentence_embeddings = self.model.encode(resume_sentences, convert_to_tensor=True)
            
            # Compute cosine similarities
            cosine_scores = util.cos_sim(jd_embedding, sentence_embeddings)[0]
            
            # Find max similarity
            max_score = torch.max(cosine_scores)
            best_idx = torch.argmax(cosine_scores)
            
            if max_score > 0.60: # Lowered threshold based on testing (0.61 for explicit sentence)
                return {
                    "match": True,
                    "confidence": float(max_score),
                    "evidence": resume_sentences[best_idx].strip()
                }
                
        except Exception as e:
             print(f"Error in semantic matching: {e}")
             
        return {"match": False, "confidence": 0, "evidence": None}
    
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

    def score(self, resume_skills: List[str], jd_data: Dict[str, List[str]], resume_sentences: List[str] = []) -> Dict:
        """
        Calculates the relevance score with Rule-based, Contextual, and Semantic matching.
        """
        resume_skills_set = {self.normalize_skill(s) for s in resume_skills}
        
        # Optimization: Pre-compute sentence embeddings once
        cached_embeddings = None
        if self.model and resume_sentences:
            try:
                cached_embeddings = self.model.encode(resume_sentences, convert_to_tensor=True)
            except Exception as e:
                print(f"Warning: Failed to pre-compute embeddings: {e}")
        
        # Refine JD skills
        must_have_skills = self.extract_skills_from_jd(jd_data['must_have'])
        good_to_have_skills = self.extract_skills_from_jd(jd_data['good_to_have'])
        
        # Lists for detailed report
        matches = {
            "exact": [],
            "contextual": [],
            "semantic": [],
            "missing": []
        }
        
        current_score = 0
        total_possible = 0
        
        # Helper to process a skill group
        def process_skills(target_skills, weight_category):
            nonlocal current_score, total_possible
            
            category_weight = self.weights[weight_category]
            
            for skill in target_skills:
                skill_total_val = category_weight # Baselinen
                # We normalize 1.0 as max per skill for easier math, then scale
                
                # Check Exact Match
                if self.normalize_skill(skill) in resume_skills_set:
                    # EXACT MATCH
                    # Check Contextual Bonus
                    ctx = self.is_contextual(skill, resume_sentences)
                    score_boost = 1.0
                    match_type = "Exact"
                    
                    if ctx['contextual']:
                        score_boost += 0.3
                        matches['contextual'].append({"skill": skill, "evidence": ctx['evidence']})
                        
                    current_score += (category_weight * score_boost)
                    matches['exact'].append(skill)
                    
                else:
                    # MISSING - Try Semantic Recovery
                    sem = self.find_semantic_match(skill, resume_sentences, cached_sentence_embeddings=cached_embeddings)
                    if sem['match']:
                        # Recovered!
                        score_boost = 0.6
                        current_score += (category_weight * score_boost)
                        matches['semantic'].append({
                            "skill": skill,
                            "evidence": sem['evidence'],
                            "confidence": sem['confidence']
                        })
                    else:
                        matches['missing'].append(skill)
                
                # Update total possible (max potential for this skill was weight * (1.0 + 0.3))
                # Actually, standardizing total possible:
                # If we want 100% to be achievable with just exact matches, base total on 1.0 * weight
                # Boosts allow >100% or help recover.
                # Let's say Total Possible is simply Sum(Weights).
                total_possible += category_weight

        process_skills(must_have_skills, 'must_have')
        process_skills(good_to_have_skills, 'good_to_have')
        
        # Calculate Final Score
        if total_possible == 0:
            final_score = 0
        else:
            final_score = (current_score / total_possible) * 100
            
        # Phase 5: Penalties
        # if missing must have ratio > 0.4 -> penalize
        if must_have_skills:
            missing_must = len([s for s in matches['missing'] if s in must_have_skills])
            if (missing_must / len(must_have_skills)) > 0.4:
                final_score *= 0.6
                
        # Phase 6: Verdict
        if final_score >= 75:
            verdict = "Strong Fit"
        elif final_score >= 50:
            verdict = "Moderate Fit"
        else:
            verdict = "Weak Fit"
            
        return {
            "score": round(final_score, 2),
            "verdict": verdict,
            "breakdown": matches,
            "details": {
                "total_must_have": len(must_have_skills),
                "total_good_to_have": len(good_to_have_skills)
            }
        }
