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
            'business analyst', 'research scientist',
            
            # Design & Product
            'ui/ux designer', 'product designer', 'graphic designer',
            'product manager', 'project manager',
            
            # Internships & Entry Level
            'intern', 'trainee', 'associate', 'junior developer',
            'software intern', 'data science intern', 'sde intern',
            
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
        
        # 1. Fix: "DeveloperManager" -> "Developer Manager" 
        # (Capital letter following lowercase, but mostly for English words)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # 2. Fix: "Experience.," -> "Experience ., " -> "Experience,"
        # Add space after punctuation if missing
        text = re.sub(r'([.,;:!?])([A-Za-z])', r'\1 \2', text)
        
        # 3. Fix: "1st", "2nd" being split
        text = re.sub(r'(\d)(st|nd|rd|th)', r'\1\2', text)
        
        # 4. UNIVERSAL FIX: Repair common Tech Stack names damaged by step 1 or PDF extraction
        # This list covers common technologies that are often CamelCase or have specific spacing
        replacements = {
            # Languages
            r'Java\s*Script': 'JavaScript',
            r'Type\s*Script': 'TypeScript',
            r'Coffee\s*Script': 'CoffeeScript',
            
            # Frameworks & Libs
            r'Node\s*\.\s*js': 'Node.js',
            r'React\s*Js': 'React.js',
            r'Vue\s*Js': 'Vue.js',
            r'Next\s*Js': 'Next.js',
            r'Nest\s*Js': 'Nest.js',
            r'Express\s*Js': 'Express.js',
            r'Angular\s*Js': 'AngularJS',
            r'Tensor\s*Flow': 'TensorFlow',
            r'Py\s*Torch': 'PyTorch',
            r'Sci\s*Kit': 'Scikit',
            r'Mat\s*Plot\s*Lib': 'Matplotlib',
            r'Power\s*BI': 'PowerBI',
            
            # Databases
            r'Mongo\s*DB': 'MongoDB',
            r'Postgre\s*SQL': 'PostgreSQL',
            r'My\s*SQL': 'MySQL',
            r'No\s*SQL': 'NoSQL',
            r'Dynamo\s*DB': 'DynamoDB',
            r'Cosmos\s*DB': 'CosmosDB',
            
            # Tools
            r'Git\s*Hub': 'GitHub',
            r'Git\s*Lab': 'GitLab',
            r'Vs\s*Code': 'VS Code',
            r'Visual\s*Studio': 'Visual Studio',
            
            # Concepts
            r'Back\s*End': 'Backend',
            r'Front\s*End': 'Frontend',
            r'Full\s*Stack': 'FullStack',
            r'Dev\s*Ops': 'DevOps',
            r'Ci\s*/\s*Cd': 'CI/CD',
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
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
  
    
    # def extract_education(self, edu_lines):
    #     """Extract education details - focusing on college/university degree only."""
    #     education_list = []
    #     current_edu = {}
    
    #     # Keywords that indicate 12th/HSC (high school) - we'll skip these
    #     school_indicators = ['xii', '12th', 'hsc', 'higher secondary', 'junior college', 
    #                     'senior secondary', 'intermediate', 'pre-university']
    
    #     i = 0
    #     while i < len(edu_lines):
    #         line = edu_lines[i].strip()
    #         line_lower = line.lower()
        
    #         print("line : ", i, " : ", line_lower)
        
    #     # Skip empty lines
    #         if not line:
    #             i += 1
    #             continue
        
    #         # Check if this line is about 12th/HSC - skip entire entry
    #         is_school = any(indicator in line_lower for indicator in school_indicators)
    #         if is_school:
    #             # Save current entry before skipping
    #             if current_edu and 'course' in current_edu:
    #                 education_list.append(current_edu)
    #                 current_edu = {}
    #             i += 1
    #             continue
            
    #         # Look for degree patterns
    #         degree_pattern = r'\b(b\.?\s*tech|bachelor|b\.?\s*e\.?|m\.?\s*tech|master|mba|bca|mca|phd)\b'
            
    #         # Also match concatenated versions like "btechin"
    #         degree_match = re.search(degree_pattern, line, re.IGNORECASE)
    #         if not degree_match:
    #             # Try without word boundary for concatenated text
    #             degree_match = re.search(r'(b\.?tech|btech|bachelor|b\.?e\.?|m\.?tech|mtech|master|mba|bca|mca|phd)', 
    #                                     line, re.IGNORECASE)
            
    #         if degree_match:
    #             # Start new education entry if we already have one
    #             if current_edu and 'course' in current_edu:
    #                 education_list.append(current_edu)
    #                 current_edu = {}
                
    #             # Extract course name
    #             specialization_match = re.search(
    #                 r'(computer science|information technology|data science|electronics|mechanical|electrical|civil|computer engineering)', 
    #                 line, re.IGNORECASE
    #             )
                
    #             print("specialization_match : ", specialization_match)
                
    #             if specialization_match:
    #                 degree = degree_match.group(0).strip()
    #                 specialization = specialization_match.group(0).strip()
    #                 current_edu['course'] = f"{degree} in {specialization}".title()
    #             else:
    #                 current_edu['course'] = degree_match.group(0).strip().title()
                
    #             # Look for years in this line
    #             year_matches = re.findall(r'\b(20\d{2})\b', line)
    #             if year_matches:
    #                 current_edu['graduation_year'] = year_matches[-1]
            
    #         # Look for college/university (independent of degree line)
    #         # Look for college in the same line
    #             college_keywords = ['institute', 'university', 'college', 'academy']
    #             for keyword in college_keywords:
    #                 if keyword in line_lower:
    #                     # Extract college name: try to get the clean name
    #                     # Pattern: look for capitalized words around the keyword
    #                     college_match = re.search(
    #                         r'([A-Z][a-zA-Z\s\.]+(?:' + keyword + r')[a-zA-Z\s\.]*)',
    #                         line, re.IGNORECASE
    #                     )
    #                     if college_match:
    #                         college_name = college_match.group(0).strip()
    #                         # Remove dates from college name
    #                         college_name = re.sub(r'\b(20\d{2}|19\d{2})\b', '', college_name).strip()
    #                         # Remove extra spaces and hyphens
    #                         college_name = re.sub(r'\s+', ' ', college_name)
    #                         college_name = re.sub(r'\s*[-–]\s*$', '', college_name).strip()
    #                         current_edu['college'] = college_name
    #                         break
            
    #         i += 1
    
    #     # Append the last entry
    #     if current_edu and 'course' in current_edu:
    #         education_list.append(current_edu)
        
    #     return education_list

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
        return education_list

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
        """Helper method to extract technologies from a single line."""
        line_lower = line.lower()
        # tech_list = []
        
        # Pattern 1: Explicit "Tech:" or "Technologies Used:"
        tech_pattern = r'(tech(?:nologies)?(?:\s+used)?|built\s+with|stack)[:\s]*(.+)'
        match = re.search(tech_pattern, line, re.IGNORECASE)
        
        if match:
            tech_string = match.group(2)
            # Split by comma
            techs = re.split(r'[,]', tech_string)
            for tech in techs:
                tech_clean = tech.strip().lower()
                # Remove common words
                tech_clean = re.sub(r'\b(and|or|with)\b', '', tech_clean).strip()
                
                # Match against known skills
                for known_skill in self.known_skills:
                    if len(known_skill) <= 3:
                        # For short words, require exact word match with word boundaries
                        pattern = r'\b' + re.escape(known_skill) + r'\b'
                        if re.search(pattern, tech_clean):
                            tech_list.append(known_skill)
                    else:
                        # For longer words, substring match is fine
                        if known_skill in tech_clean:
                            tech_list.append(known_skill)
        

    # def find_role_in_text(self, text):
    #     """Find a job role in the given text."""
    #     text_lower = text.lower()
        
    #     # Check for exact role matches
    #     for role in self.known_roles:
    #         if role in text_lower:
    #             return role.title()
        
    #     # Check for partial matches with common role keywords
    #     role_keywords = ['developer', 'engineer', 'intern', 'analyst', 
    #                     'designer', 'manager', 'lead', 'architect',
    #                     'contributor', 'member', 'coordinator']
        
    #     for keyword in role_keywords:
    #         pattern = r'\b(\w+\s+)?' + keyword + r'(\s+\w+)?\b'
    #         match = re.search(pattern, text_lower)
    #         if match:
    #             return match.group(0).strip().title()
        
    #     return None
    

    # def extract_experience(self, exp_lines):
    #     """Extract work experience/internship details."""
    #     experiences = []
    #     i = 0
        
    #     while i < len(exp_lines):
    #         line = exp_lines[i].strip()
            
    #         # Skip bullet points and short lines
    #         if line.startswith('•') or line.startswith('-') or len(line) < 5:
    #             i += 1
    #             continue
            
    #         # Look for lines that might contain company and role
    #         # Pattern 1: "Company Name, Role"
    #         # Pattern 2: "Company Name - Role"
    #         # Pattern 3: "Role at Company Name"
            
    #         company = None
    #         role = None
    #         time_period = None
            
    #         # Check if line has company/role pattern
    #         if ',' in line or '–' in line or ' - ' in line:
    #             # Split by comma or dash
    #             parts = re.split(r'[,–\-]', line, maxsplit=1)
                
    #             if len(parts) >= 2:
    #                 part1 = parts[0].strip()
    #                 part2 = parts[1].strip()
                    
    #                 # Check which part is role
    #                 role1 = self.find_role_in_text(part1)
    #                 role2 = self.find_role_in_text(part2)
                    
    #                 if role2:
    #                     company = part1
    #                     role = role2
    #                 elif role1:
    #                     role = role1
    #                     company = part2
    #                 else:
    #                     # Default: first part is company
    #                     company = part1
    #                     role = part2
    #         else:
    #             # Single line - try to extract role from it
    #             potential_role = self.find_role_in_text(line)
    #             if potential_role:
    #                 role = potential_role
    #                 # Remove role from line to get company
    #                 company = re.sub(re.escape(potential_role), '', line, flags=re.IGNORECASE).strip()
    #                 company = re.sub(r'[,\-–]', '', company).strip()
    #             else:
    #                 company = line
            
    #         # Look ahead for date/time period in next few lines
    #         for j in range(i + 1, min(i + 4, len(exp_lines))):
    #             next_line = exp_lines[j].strip()
                
    #             # Date patterns
    #             date_patterns = [
    #                 r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'`]*\d{2,4}\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'`]*\d{2,4}",
    #                 r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'`]*\d{2,4}\s*[-–]\s*(present|current)",
    #                 r"\d{4}\s*[-–]\s*\d{4}",
    #                 r"\d{4}\s*[-–]\s*(present|current)"
    #             ]
                
    #             for pattern in date_patterns:
    #                 match = re.search(pattern, next_line, re.IGNORECASE)
    #                 if match:
    #                     time_period = match.group(0)
    #                     break
                
    #             if time_period:
    #                 break
            
    #         # Only add if we have at least company or role
    #         if company or role:
    #             experiences.append({
    #                 'company': company if company else None,
    #                 'role': role if role else None,
    #                 'time_period': time_period
    #             })
            
    #         i += 1
        
    #     # Remove duplicates and invalid entries
    #     seen = set()
    #     filtered_experiences = []
    #     for exp in experiences:
    #         # Create a unique key
    #         key = (exp['company'], exp['role'])
    #         if key not in seen and (exp['company'] or exp['role']):
    #             seen.add(key)
    #             filtered_experiences.append(exp)
        
    #     return filtered_experiences
    

    def parse(self, file_path):
        """Main parsing function."""
        # Extract text
        text = self.extract_text(file_path)
        return self.parse_text(text)

    def parse_text(self, text):
        """Parse structured data from text."""
        # Extract basic info
        basic_info = self.extract_basic_info(text)
        
        # Split into sections
        sections = self.split_into_sections(text)
        print("projects : ", sections['projects'])
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
            'sentences': re.split(r'[.\n•]', text) if text else []
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