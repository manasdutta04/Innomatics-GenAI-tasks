from langchain_core.prompts import PromptTemplate

extract_prompt = PromptTemplate(
    template="""You are an expert HR Data Extractor.
Extract the Name, Skills, Experience, and Tools exactly as they appear in the provided Resume.
Do NOT assume info not present in the Resume.

Return the output in ONLY valid JSON format with the keys: "name", "skills", "experience", and "tools".

Resume: {resume}
""",
    input_variables=["resume"]
)

match_prompt = PromptTemplate(
    template="""You are an expert HR Analyst.
Compare the extracted candidate profile with the Job Description.

Job Description: {job_description}

Extracted Candidate Profile:
{extracted_info}

Analyze how well the candidate's Skills, Experience, and Tools match the required job described. Be objective and identify matching and missing requirements clearly.
""",
    input_variables=["job_description", "extracted_info"]
)

score_prompt = PromptTemplate(
    template="""You are a strict Recruiter.
Based on the provided matching analysis between a candidate profile and a job description, assign a match score between 0 and 100.

EXAMPLES:
Match Analysis: The candidate has 3 years of experience in Python and SQL but is entirely lacking Machine Learning skills.
Score: 45

Match Analysis: The candidate meets all the requirements perfectly, including 5 years in Data Science, AWS expertise, and proficiency in Scikit-Learn.
Score: 95

Return ONLY a valid JSON object with a single key "score" and an integer value.

Match Analysis:
{match_analysis}""",
    input_variables=["match_analysis"]
)

explain_prompt = PromptTemplate(
    template="""You are an HR Explainer AI.
Based on the candidate matching analysis and the calculated score, provide a brief reasoning for why this score was assigned.
Do not hallucinate info.

Score Assigned: {score}

Match Analysis:
{match_analysis}

Return ONLY a valid JSON object with a single key "explanation" containing your text.
""",
    input_variables=["score", "match_analysis"]
)
