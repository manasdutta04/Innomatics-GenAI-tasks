import os
import json
from dotenv import load_dotenv
from chains.resume_chain import ResumeScreeningChain
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# Load env variables (LangSmith API keys, HF Token)
load_dotenv()

# Test Data
job_description = """
Data Scientist Role:
- 3+ years experience in Data Science.
- Strong skills in Python, SQL, and Machine Learning (Scikit-Learn, TensorFlow/PyTorch).
- Experience with large-scale data processing tools like Spark.
- Cloud platforms (AWS or GCP) experience.
- Strong analytical and communication skills.
"""

strong_candidate_resume = """
Name: Alice Smith
Profile: Senior Data Scientist with 4 years of experience.
Experience:
- Data Scientist at TechCorp (4 years): Developed predictive models, handled big data with Apache Spark.
- Cloud Deployment on AWS.
Skills: Python, SQL, Machine Learning.
Tools: Scikit-Learn, PyTorch, TensorFlow, AWS, Spark, Git.
"""

average_candidate_resume = """
Name: Bob Jones
Profile: Data Analyst transitioning to Data Science. 2 years experience.
Experience:
- Data Analyst at FinanceInc: Worked on SQL queries, basic Python scripts, and created dashboards.
Skills: Python, SQL, Data Visualization, basic statistical modeling.
Tools: Tableau, Excel, Pandas, Scikit-Learn.
"""

weak_candidate_resume = """
Name: Charlie Brown
Profile: Software Engineer specialized in Frontend development. 5 years experience.
Experience:
- Frontend Dev at WebSolutions: Built interactive UI.
Skills: JavaScript, React, HTML, CSS.
Tools: VS Code, Git, NPM.
"""

def main():
    # Setup LLM using HuggingFace Endpoint
    llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-72B-Instruct",
        temperature=0.1,
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
    )
    
    chat_model = ChatHuggingFace(llm=llm)
    
    screening_system = ResumeScreeningChain(chat_model)

    candidates = {
        "Strong Candidate": strong_candidate_resume,
        "Average Candidate": average_candidate_resume,
        "Weak Candidate": weak_candidate_resume
    }

    all_results = {}

    for name, resume in candidates.items():
        console.print(f"\n[bold cyan]{'='*50}\nProcessing {name}\n{'='*50}[/bold cyan]")
        result = screening_system.process_candidate(resume, job_description)
        
        extracted_name = result['extracted_info'].get('name', 'Unknown Candidate')
        console.print(f"\n[bold green]✅ Extracted Candidate Name:[/bold green] {extracted_name}")
        
        console.print(Panel(json.dumps(result['extracted_info'], indent=2), title="Extracted Info", border_style="cyan"))
        
        console.print("\n[bold magenta]--- Match Analysis ---[/bold magenta]")
        console.print(Markdown(result['match_analysis']))
        
        console.print(f"\n[bold yellow]--- Score ---[/bold yellow]\n[bold]{result['score']}[/bold]")
        
        console.print("\n[bold blue]--- Explanation ---[/bold blue]")
        console.print(result['explanation'])

        # Store result for saving
        all_results[name] = result

    # Save to a local JSON file
    output_path = os.path.join("data", "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
        
    # Save to a local TXT file
    txt_output_path = os.path.join("data", "results.txt")
    with open(txt_output_path, "w", encoding="utf-8") as f:
        for candidate, data in all_results.items():
            f.write(f"{'='*50}\nCandidate: {candidate}\n{'='*50}\n")
            f.write(f"Extracted Name: {data['extracted_info'].get('name', 'Unknown')}\n")
            f.write(f"Score: {data['score']}\n\n")
            f.write("--- Match Analysis ---\n")
            f.write(f"{data['match_analysis']}\n\n")
            f.write("--- Explanation ---\n")
            f.write(f"{data['explanation']}\n\n")
            f.write("\n")

    print(f"\nAll results have been successfully saved to {output_path} and {txt_output_path}!")

if __name__ == "__main__":
    main()
