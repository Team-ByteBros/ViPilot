import pdfplumber
from docx import Document
import re
import json

class ResumeParser:
    """
    A robust resume parser that extracts structured information from resumes
    in PDF or DOCX format.
    """
    
    def __init__(self):
        # Common section headers (case-insensitive)
        self.section_patterns = {
            'education': r'\b(education|academic|qualification)\b',
            'experience': r'\b(experience|work|employment|internship)\b',
            'projects': r'\b(projects?|portfolio)\b',
            'skills': r'\b(skills?|technical|technologies|competencies)\b',
            'achievements': r'\b(achievements?|certifications?|awards?)\b'
        }
        
        # Common job roles/positions
        self.known_roles = {
            # Software Development
            'software engineer', 'software developer', 'full stack developer',
            'frontend developer', 'backend developer', 'web developer',
            'mobile developer', 'android developer', 'ios developer',
            'frontend engineer', 'backend engineer', 'full stack engineer',
            
            # Data & AI
            'data scientist', 'data analyst', 'data engineer',
            'machine learning engineer', 'ai engineer', 'ml engineer',
            'business analyst', 'research scientist', 'artificial intelligence intern',
            
            # Design & Product
            'ui/ux designer', 'product designer', 'graphic designer',
            'product manager', 'project manager',
            
            # Internships & Entry Level
            'intern', 'trainee', 'associate', 'junior developer',
            'software intern', 'data science intern', 'sde intern', 'cloud application developer trainee',
            
            # Leadership & Management
            'team lead', 'tech lead', 'engineering manager',
            'senior developer', 'senior engineer', 'lead developer',
            
            # DevOps & Cloud
            'devops engineer', 'cloud engineer', 'sre', 'site reliability engineer',
            'cloud architect', 'systems engineer',
            
            # Other Technical
            'qa engineer', 'test engineer', 'security engineer',
            'database administrator', 'network engineer',
            
            # Student Roles
            'contributor', 'volunteer', 'member', 'coordinator',
            'core member', 'technical team member', 'web developer',
            'app developer', 'research assistant'
        }
        
        # Add these missing technologies to known_skills:
        self.known_skills = {
            # Languages
            'python', 'java', 'javascript', 'c++', 'c', 'kotlin', 'sql', 
            'typescript', 'go', 'rust', 'php', 'swift', 'r', 'scala',
            
            # Frameworks & Libraries
            'react', 'reactjs', 'react.js', 'angular', 'vue', 'vue.js',
            'node.js', 'nodejs', 'express', 'express.js', 'django', 'flask',
            'fastapi', 'spring', 'spring boot', 'tensorflow', 'pytorch',
            'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
            'next.js', 'nextjs', 'streamlit', 'jetpack compose',
            'ktor', 'room', 'hilt',  # ✅ Add Android libraries
            
            # Databases
            'mongodb', 'mysql', 'postgresql', 'firebase', 'redis',
            'supabase', 'oracle', 'cassandra', 'dynamodb', 'firestore',  # ✅ Add firestore
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd',
            'jenkins', 'github actions', 'terraform', 'ansible',
            
            # Tools & Others
            'git', 'github', 'gitlab', 'postman', 'jira', 'linux',
            'tableau', 'power bi', 'powerbi', 'excel', 'kafka',
            'opencv', 'selenium', 'websocket', 'rest api', 'graphql',
            'jwt', 'razorpay',  # ✅ Add payment/auth tools
            
            # AI/ML Tools
            'gemini', 'openai', 'pinecone', 'langchain',  # ✅ Add AI tools
            
            # Concepts
            'machine learning', 'deep learning', 'nlp', 'data science',
            'data analysis', 'cloud computing', 'devops', 'agile',
            'oop', 'oops', 'etl', 'computer vision', 'rag'  # ✅ Add RAG
        }
    
    def fix_spacing(self, text):
        """Fix spacing issues in PDF extracted text."""
        # Add space before capital letters that follow lowercase letters
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        # Add space after punctuation if missing
        text = re.sub(r'([.,;:!?])([A-Za-z])', r'\1 \2', text)
        # Fix common concatenations
        text = re.sub(r'(\d)(st|nd|rd|th)', r'\1\2', text)
        return text
    
    def extract_text(self, file_path):
        """Extract text from PDF or DOCX file."""
        if file_path.endswith('.pdf'):
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            # Fix spacing issues
            text = self.fix_spacing(text)
            return text
        
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
    
    def extract_basic_info(self, text):
        """Extract name, email, and phone number."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Extract email
        # email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(r"\S+@\S+", text)
        email = email_match.group() if email_match else None
        
        # Extract phone (supports various formats)
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\b\d{10}\b',
            r'\+\d{2}\s?\d{10}'
        ]
        phone = None
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                phone = phone_match.group().strip()
                break
        
        # Extract name (first non-empty line, excluding email/phone)
        name = None
        for line in lines[:5]:
            if email and email in line:
                continue
            if phone and phone in line:
                continue
            if re.search(r'\b(resume|cv|curriculum)\b', line, re.IGNORECASE):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and all(w.replace('.', '').isalpha() for w in words):
                name = line
                break
            elif len(words) == 1 and words[0].isalpha() and len(words[0]) > 2:
                name = line
                break
        
        return {
            'name': name,
            'email': email,
            'phone': phone
        }
    
    def split_into_sections(self, text):
        """Split resume text into sections and extract technologies from projects."""
        sections = {
            'education': [],
            'experience': [],
            'projects': [],
            'skills': [],
            'achievements': [],
            'project_technologies': [],  # ✅ New: Store tech found in projects
            'raw_text': []
        }
        
        current_section = 'raw_text'
        lines = text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if line is a section header
            line_lower = line_stripped.lower()
            section_found = False
            
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line_lower, re.IGNORECASE) and len(line_stripped) < 50:
                    current_section = section_name
                    section_found = True
                    break
            
            if not section_found:
                sections[current_section].append(line_stripped)
                
                # ✅ If we're in projects section, extract technologies
                if current_section == 'projects':
                    self._extract_tech_from_line(line_stripped, sections['project_technologies'])
        
        return sections  
    
    def extract_skills(self, skill_lines, project_techs, full_text):
        """Extract technical skills from the skills section and merge with project technologies."""
        skills = set()
        
        # Extract from skills section
        for line in skill_lines:
            line_lower = line.lower()
            
            # Check for each known skill
            for skill in self.known_skills:
                if len(skill) <= 3:
                    # Word boundary for short words
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, line_lower):
                        skills.add(skill.title())
                else:
                    if skill in line_lower:
                        skills.add(skill.title())
            
            # Extract from comma/bullet separated lists
            if any(sep in line for sep in [',', '•', '·', '-', ':']):
                parts = re.split(r'[,•·:\-]', line)
                for part in parts:
                    part_clean = part.strip().lower()
                    part_clean = re.sub(r'^(languages|frameworks|tools|databases|cloud)\s*', '', part_clean)
                    if part_clean in self.known_skills and len(part_clean) > 2:
                        skills.add(part.strip().title())
        
        # ✅ Add technologies found in projects
        for tech in project_techs:
            skills.add(tech.title())
        
        # Also scan full text for skills if skills section is empty
        if not skills:
            text_lower = full_text.lower()
            for skill in self.known_skills:
                if skill in text_lower:
                    skills.add(skill.title())
        
        return sorted(list(skills))
  
    

    def extract_education(self, edu_lines):
        """Extract education details - focusing on college/university degree only."""
    
        education_list = []
        current_edu = {}
        school_indicators = [
            'xii', '12th', 'hsc', 'higher secondary', 'junior college',
            'senior secondary', 'intermediate', 'pre-university']

        i = 0

        while i < len(edu_lines):
            line = edu_lines[i].strip()
            line_lower = line.lower()
            # print("line ",i ," : ", line)
            if not line:
                i+=1
                continue

            is_school = any(indicator in line_lower for indicator in school_indicators)
            if is_school:
                if current_edu and 'course' in current_edu:
                    education_list.append(current_edu)
                    current_edu = {}
                i+=1
                continue

            degree_pattern = r'\b(b\.?\s*tech|bachelor|b\.?\s*e\.?|m\.?\s*tech|master|mba|bca|mca|phd)\b'
            degree_match = re.search(degree_pattern, line, re.IGNORECASE)
            # print("degree_match : ", degree_match)
            if not degree_match:
                degree_match = re.search(
                    r'(b\.?tech|btech|b-tech|bachelor|b\.?e\.?|m\.?tech|mtech|master|mba|bca|mca|phd)',
                    line,
                    re.IGNORECASE
                )
                # print("degree_match 2 : ", degree_match)

            if degree_match:
                if current_edu and 'course' in current_edu:
                    education_list.append(current_edu)
                    current_edu = {}
                
                specialization_match = re.search(
                    r'(computer science|computer science and engineering (data science)|information technology|data science|electronics|mechanical|'
                    r'electrical|civil|computer engineering)',
                    line,
                    re.IGNORECASE)

                degree = degree_match.group(0).strip()
                # print("degree :(380) ", degree)

                if specialization_match:
                    specialization = specialization_match.group(0).strip()
                    current_edu['course'] = f"{degree} in {specialization}".title()
                else:
                    current_edu['course'] = degree.title()

            college_keywords = ['institute', 'university', 'college', 'academy']
            if any(keyword in line_lower for keyword in college_keywords) and 'college' not in current_edu:
                college_match = re.search(
                    r'([A-Z][a-zA-Z\s\.]+(?:institute|university|college|academy)[a-zA-Z\s,\.]*)',
                    line,
                    re.IGNORECASE
                )

                if college_match:
                    college_name = college_match.group(0).strip()

                    college_name = re.sub(r'\b(20\d{2}|19\d{2})\b', '', college_name)
                    college_name = re.sub(
                        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}',
                        '',
                        college_name,
                        flags=re.IGNORECASE
                    )
                    college_name = re.sub(
                        r'[–—-]\s*(present|current).*$', '',
                        college_name,
                        flags=re.IGNORECASE
                    )
                    college_name = re.sub(r'\s+', ' ', college_name).strip()
                    college_name = re.sub(r',\s*$', '', college_name).strip()

                    current_edu['college'] = college_name

            year_matches = re.findall(r'\b(20\d{2})\b', line)
            if year_matches and 'graduation_year' not in current_edu:
                current_edu['graduation_year'] = year_matches[-1]
            
            cgpa_match = re.search(r'cgpa[:\-\s]*([0-9.]+)', line_lower)
            if cgpa_match:
                current_edu['cgpa'] = cgpa_match.group(1)
            
            i += 1

        if current_edu and 'course' in current_edu:
            education_list.append(current_edu)
            
        # Normalize to ensure all keys exist
        final_list = []
        for edu in education_list:
            final_list.append({
                'course': edu.get('course'),
                'college': edu.get('college'),
                'graduation_year': edu.get('graduation_year'),
                'cgpa': edu.get('cgpa')
            })
            
        return final_list

    # def extract_tech_from_projects(self, project_lines):
    #     """Extract technologies mentioned in project descriptions."""
    #     technologies = set()
        
    #     i = 0
    #     while i < len(project_lines):
    #         line = project_lines[i].strip()
    #         line_lower = line.lower()
            
    #         # Pattern 1: Explicit "Tech:" or "Technologies Used:"
    #         tech_pattern = r'(tech(?:nologies)?(?:\s+used)?|built\s+with|stack)[:\s]*(.+)'
    #         match = re.search(tech_pattern, line, re.IGNORECASE)
    #         if match:
    #             tech_string = match.group(2)
    #             # Extract technologies from comma/pipe separated list
    #             techs = re.split(r'[,|]', tech_string)
    #             for tech in techs:
    #                 tech_clean = tech.strip().lower()
    #                 # Remove common words
    #                 tech_clean = re.sub(r'\b(and|or|with)\b', '', tech_clean).strip()
                    
    #                 # Check if it's a known skill (with word boundary to avoid partial matches)
    #                 for known_skill in self.known_skills:
    #                     # Use word boundary for short words to avoid false matches
    #                     if len(known_skill) <= 3:
    #                         # For short words like "go", "r", etc., require exact word match
    #                         pattern = r'\b' + re.escape(known_skill) + r'\b'
    #                         if re.search(pattern, tech_clean):
    #                             technologies.add(known_skill.title())
    #                     else:
    #                         # For longer words, simple substring match is fine
    #                         if known_skill in tech_clean:
    #                             technologies.add(known_skill.title())
            
    #         # Pattern 2: Technologies after dash (–) in project title
    #         # Example: "Project Name – Tech Stack" or "Project Name - Tech1, Tech2"
    #         if ('–' in line or ' - ' in line) and not re.search(tech_pattern, line, re.IGNORECASE):
    #             # Split by dash
    #             parts = re.split(r'[–-]', line)
    #             if len(parts) >= 2:
    #                 # Check if the last part contains technologies
    #                 last_part = parts[-1].strip()
                    
    #                 # If it contains common tech keywords or commas, it's likely tech stack
    #                 if ',' in last_part or any(skill in last_part.lower() for skill in ['react', 'python', 'node', 'kotlin', 'java']):
    #                     techs = re.split(r'[,]', last_part)
    #                     for tech in techs:
    #                         tech_clean = tech.strip().lower()
                            
    #                         # Match against known skills
    #                         for known_skill in self.known_skills:
    #                             if len(known_skill) <= 3:
    #                                 pattern = r'\b' + re.escape(known_skill) + r'\b'
    #                                 if re.search(pattern, tech_clean):
    #                                     technologies.add(known_skill.title())
    #                             else:
    #                                 if known_skill in tech_clean:
    #                                     technologies.add(known_skill.title())
            
    #         # Pattern 3: Look for lines that start with bullet and contain "Tech" keyword
    #         if line.startswith('•') or line.startswith('-'):
    #             if 'tech' in line_lower:
    #                 # Extract everything after "tech:"
    #                 tech_match = re.search(r'tech[:\s]+(.+)', line, re.IGNORECASE)
    #                 if tech_match:
    #                     tech_string = tech_match.group(1)
    #                     techs = re.split(r'[,|]', tech_string)
    #                     for tech in techs:
    #                         tech_clean = tech.strip().lower()
                            
    #                         for known_skill in self.known_skills:
    #                             if len(known_skill) <= 3:
    #                                 pattern = r'\b' + re.escape(known_skill) + r'\b'
    #                                 if re.search(pattern, tech_clean):
    #                                     technologies.add(known_skill.title())
    #                             else:
    #                                 if known_skill in tech_clean:
    #                                     technologies.add(known_skill.title())
            
    #         i += 1
        
    #     return sorted(list(technologies))


    def _extract_tech_from_line(self, line, tech_list):
        line_lower = line.lower()

        # ---------- Pattern 1: Explicit "Tech / Technologies used" ----------
        tech_pattern = r'(tech(?:nologies)?(?:\s+used)?|built\s+with|stack)[:\s]*(.+)'
        match = re.search(tech_pattern, line, re.IGNORECASE)

        tech_string = None

        if match:
            tech_string = match.group(2)

        # ---------- Pattern 2: Project title | Tech1, Tech2 ----------
        elif '|' in line:
            parts = line.split('|', 1)
            if len(parts) == 2:
                tech_string = parts[1]

        # ---------- Extract technologies ----------
        if tech_string:
            techs = re.split(r'[,/]', tech_string)
            for tech in techs:
                tech_clean = tech.strip().lower()

                for known_skill in self.known_skills:
                    if len(known_skill) <= 3:
                        if re.search(r'\b' + re.escape(known_skill) + r'\b', tech_clean):
                            tech_list.append(known_skill)
                    else:
                        if known_skill in tech_clean:
                            tech_list.append(known_skill)

    
    def extract_experience(self, exp_lines):
        """Extract work experience - role and months worked."""
        experiences = []
        
        i = 0
        while i < len(exp_lines):
            line = exp_lines[i].strip()
            line_lower = line.lower()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Skip bullet points (these are descriptions, not roles)
            if line.startswith('•') or line.startswith('●') or line.startswith('-') or line.startswith('○'):
                i += 1
                continue
            
            # Skip lines that are clearly descriptions (contain common description words)
            description_indicators = [
                'developed', 'worked', 'completed', 'gained', 'implemented',
                'created', 'built', 'designed', 'managed', 'led', 'achieved',
                'leveraged', 'integrated', 'deployed', 'features', 'include'
            ]
            
            # If line starts with description words, skip it
            first_word = line_lower.split()[0] if line_lower.split() else ''
            if first_word in description_indicators:
                i += 1
                continue
            
            # Skip if line contains percentage or numbers like "92 percent accuracy"
            if re.search(r'\d+\s*(percent|%|accuracy)', line_lower):
                i += 1
                continue
            
            # Skip lines that look like continuation of descriptions
            if line_lower.startswith(('and ', 'or ', 'including ', 'with ', 'through ')):
                i += 1
                continue
            
            # Look for date pattern in the line - this is likely a role line
            has_date = self._has_date_pattern(line)
            
            # Look for role keywords
            has_role = any(role in line_lower for role in self.known_roles)
            
            # Look for company indicators (Remote, location, |)
            has_company_indicator = '|' in line or 'remote' in line_lower
            
            # This line is likely a role if:
            # 1. It has a date pattern, OR
            # 2. It has a known role keyword, OR  
            # 3. It has company indicators AND is not too long
            is_role_line = (has_date or has_role or (has_company_indicator and len(line) < 100))
            
            if not is_role_line:
                i += 1
                continue
            
            experience_entry = {
                'role': None,
                'months': None
            }
            
            # Extract role from the line
            # Pattern: "Role Title" followed by date, or "Company | Role"
            
            # First, try to extract date from this line
            months = self._extract_duration(line)
            if months is not None:
                experience_entry['months'] = months
                
                # Remove date part to get role
                line_without_date = re.sub(
                    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\'`]*\d{2,4}\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present|current)[a-z]*[\s\'`]*\d{0,4}',
                    '',
                    line,
                    flags=re.IGNORECASE
                ).strip()
                
                # Also remove year-only patterns
                line_without_date = re.sub(r'\d{4}\s*[-–]\s*\d{4}', '', line_without_date).strip()
                
                experience_entry['role'] = line_without_date
            
            # If no date in current line, look ahead
            if experience_entry['months'] is None:
                for j in range(i + 1, min(i + 3, len(exp_lines))):
                    next_line = exp_lines[j].strip()
                    months = self._extract_duration(next_line)
                    if months is not None:
                        experience_entry['months'] = months
                        break
            
            # If still no role extracted, try pattern matching
            if not experience_entry['role']:
                # Pattern: "Company, Role" or "Role, Company"
                if ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    
                    # Check which part contains a known role
                    for part in parts:
                        part_lower = part.lower()
                        for known_role in self.known_roles:
                            if known_role in part_lower:
                                experience_entry['role'] = part
                                break
                        if experience_entry['role']:
                            break
                    
                    # If no known role found, take first part (usually role comes first)
                    if not experience_entry['role'] and len(parts) >= 1:
                        experience_entry['role'] = parts[0]
                else:
                    # Check next line for company name (if it has | or Remote)
                    if i + 1 < len(exp_lines):
                        next_line = exp_lines[i + 1].strip()
                        if '|' in next_line or 'remote' in next_line.lower():
                            # Current line is the role
                            experience_entry['role'] = line
            
            # Clean up role - remove trailing month names
            if experience_entry['role']:
                experience_entry['role'] = re.sub(
                    r'\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*$',
                    '',
                    experience_entry['role'],
                    flags=re.IGNORECASE
                ).strip()
            
            # Only add if we have a valid role
            if experience_entry['role'] and len(experience_entry['role']) > 5:
                experiences.append(experience_entry)
            
            i += 1
        
        # Remove duplicates
        seen = set()
        filtered = []
        for exp in experiences:
            key = (exp['role'], exp['months'])
            if key not in seen and exp['role']:
                seen.add(key)
                filtered.append(exp)
        
        return filtered

    def _has_date_pattern(self, line):
        """Check if line contains a date pattern."""
        date_patterns = [
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\'`]*\d{2,4}',
            r'\d{4}\s*[-–]\s*\d{4}',
            r'(present|current)'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def _extract_duration(self, line):
        """Helper to calculate months of experience from duration string."""
        from datetime import datetime
        
        # Month name to number mapping
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        # Pattern 1: "Aug'24 - Mar'25" or "Aug 2024 - Mar 2025"
        pattern1 = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'`]*(\d{2,4})\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'`]*(\d{2,4})"
        match = re.search(pattern1, line, re.IGNORECASE)
        
        if match:
            start_month = match.group(1).lower()
            start_year = match.group(2)
            end_month = match.group(3).lower()
            end_year = match.group(4)
            
            # Convert 2-digit year to 4-digit
            if len(start_year) == 2:
                start_year = '20' + start_year
            if len(end_year) == 2:
                end_year = '20' + end_year
            
            # Get month numbers
            start_month_num = month_map.get(start_month[:3])
            end_month_num = month_map.get(end_month[:3])
            
            if start_month_num and end_month_num:
                # Calculate months difference
                start_date = datetime(int(start_year), start_month_num, 1)
                end_date = datetime(int(end_year), end_month_num, 1)
                
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                return months_diff + 1  # +1 to include both start and end months
        
        # Pattern 2: "Aug'24 - Present" or "Aug 2024 - Present"
        pattern2 = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'`]*(\d{2,4})\s*[-–]\s*(present|current)"
        match = re.search(pattern2, line, re.IGNORECASE)
        
        if match:
            start_month = match.group(1).lower()
            start_year = match.group(2)
            
            # Convert 2-digit year to 4-digit
            if len(start_year) == 2:
                start_year = '20' + start_year
            
            # Get month number
            start_month_num = month_map.get(start_month[:3])
            
            if start_month_num:
                # Calculate from start to current month
                start_date = datetime(int(start_year), start_month_num, 1)
                current_date = datetime.now()
                
                months_diff = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
                return months_diff + 1
        
        # Pattern 3: "2024 - 2025" (assume full years)
        pattern3 = r"(\d{4})\s*[-–]\s*(\d{4})"
        match = re.search(pattern3, line)
        
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            
            # Calculate year difference in months
            return (end_year - start_year) * 12
        
        # Pattern 4: "Jan 2025 – April 2025"
        pattern4 = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})"
        match = re.search(pattern4, line, re.IGNORECASE)
        
        if match:
            start_month = match.group(1).lower()
            start_year = match.group(2)
            end_month = match.group(3).lower()
            end_year = match.group(4)
            
            start_month_num = month_map.get(start_month[:3])
            end_month_num = month_map.get(end_month[:3])
            
            if start_month_num and end_month_num:
                start_date = datetime(int(start_year), start_month_num, 1)
                end_date = datetime(int(end_year), end_month_num, 1)
                
                months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                return months_diff + 1
        
        return None

    def parse(self, file_path):
        """Main parsing function."""
        # Extract text
        text = self.extract_text(file_path)
        
        # Extract basic info
        basic_info = self.extract_basic_info(text)
        
        # Split into sections
        sections = self.split_into_sections(text)
        sections['project_technologies'] = list(set(sections['project_technologies']))
        
        # Extract structured data
        result = {
            'name': basic_info['name'],
            'email': basic_info['email'],
            'phone': basic_info['phone'],
            'skills': self.extract_skills(
            sections['skills'], 
            sections['project_technologies'],  # ✅ Pass project techs
            text
        ),
            'education': self.extract_education(sections['education']),
            'experience': self.extract_experience(sections['experience']) 
            # 'techs': self.extract_tech_proj(sections['projects']),
            # 'experience': self.extract_experience(sections['experience'])
        }
        
        return result
    
    def parse_to_json(self, file_path, output_file=None):
        """Parse resume and optionally save to JSON file."""
        result = self.parse(file_path)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        return result


if __name__ == "__main__":
    parser = ResumeParser()
    resume_path = "Python backend/Resumes/Meet_Oza_Resume_2.9.pdf"
    parsed_data = parser.parse(resume_path)
    print(json.dumps(parsed_data, indent=2))