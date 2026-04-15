from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from prompts.prompts import extract_prompt, match_prompt, score_prompt, explain_prompt

class ResumeScreeningChain:
    def __init__(self, llm):
        self.llm = llm
        
        # Step 1: Extract (JSON format)
        self.extract_chain = extract_prompt | self.llm | JsonOutputParser()
        
        # Step 2: Match
        self.match_chain = match_prompt | self.llm | StrOutputParser()
        
        # Step 3: Score (Few-shot prompting used in prompt + JSON format)
        self.score_chain = score_prompt | self.llm | JsonOutputParser()
        
        # Step 4: Explain (JSON Output)
        self.explain_chain = explain_prompt | self.llm | JsonOutputParser()

    def process_candidate(self, resume_text, job_description):
        print("Extracting skills...")
        extracted_info = self.extract_chain.invoke(
            {"resume": resume_text},
            config={"tags": ["candidate_extraction", "json_output"]}
        )
        
        print("Matching with Job Description...")
        match_analysis = self.match_chain.invoke(
            {
                "job_description": job_description, 
                "extracted_info": extracted_info
            },
            config={"tags": ["candidate_analysis"]}
        )
        
        print("Calculating score...")
        score_res = self.score_chain.invoke(
            {"match_analysis": match_analysis},
            config={"tags": ["candidate_scoring", "few_shot_prompt", "json_output"]}
        )
        
        print("Generating explanation...")
        explanation_res = self.explain_chain.invoke(
            {
                "score": str(score_res.get("score")),
                "match_analysis": match_analysis
            },
            config={"tags": ["candidate_explanation", "json_output"]}
        )
        
        return {
            "extracted_info": extracted_info,
            "match_analysis": match_analysis,
            "score": score_res.get("score"),
            "explanation": explanation_res.get("explanation")
        }
