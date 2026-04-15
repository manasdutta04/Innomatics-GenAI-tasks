import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# Load env variables
load_dotenv()

# --- 1. INTENTIONALLY BAD PROMPT (Missing JSON instructions) ---
# We are deliberately removing the instruction to format as JSON
bad_extract_prompt = PromptTemplate(
    template="""You are an expert HR Data Extractor.
Extract the Name, Skills, Experience, and Tools exactly as they appear in the provided Resume.
Resume: {resume}
""",
    input_variables=["resume"]
)

# --- 2. RESUME DATA ---
resume_text = """
Name: Buggy Candidate
Profile: I have 10 years of experience but I didn't write it clearly.
Skills: Python, wandering around.
"""

def main():
    print("Running Intentionally Buggy Pipeline...")
    
    # Setup LLM
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        temperature=0.1,
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
    )
    chat_model = ChatHuggingFace(llm=llm)
    
    # --- 3. PIPELINE WITH A BUG ---
    # The LLM will return plain text, but JsonOutputParser EXPECTS valid JSON.
    # This will cause an incorrect output / parsing error!
    buggy_chain = bad_extract_prompt | chat_model | JsonOutputParser()
    
    try:
        result = buggy_chain.invoke({"resume": resume_text})
        print(result)
    except Exception as e:
        print(f"\n❌ PIPELINE FAILED (This is expected!):")
        print(str(e))

if __name__ == "__main__":
    main()
