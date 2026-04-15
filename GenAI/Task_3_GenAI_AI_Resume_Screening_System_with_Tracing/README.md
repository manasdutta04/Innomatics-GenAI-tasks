# AI Resume Screening System with Tracing

An AI-powered Resume Screening system that evaluates candidate resumes against a given job description. The project utilizes **LangChain**, **LangSmith** for observability/tracing, and **HuggingFace** inference endpoints to process candidates through a modular extraction and scoring pipeline.

## Features
- **Skill Extraction:** Pulls exact skills, experience, and tools from raw text resumes and structures them into JSON format.
- **Match Analysis:** Objectively compares candidate qualifications against the job description to find matches and missing requirements.
- **Automated Scoring:** Leverages Few-Shot Prompting to assign a standardized score (0-100) based on the matching analysis.
- **Explainability:** Generates a coherent reasoning paragraph explaining *why* the candidate received their specific score.
- **Observability with LangSmith:** Full pipeline tracing capabilities including tags (`candidate_scoring`, `json_output`, etc.) to monitor LLM interactions.
- **Rich Terminal Output:** Beautifully formatted console logs using the `rich` library.
- **Data Export:** Automatically saves evaluation reports into `data/results.json` and `data/results.txt`.

## Tech Stack
- **Python 3.x**
- **LangChain** (LCEL - LangChain Expression Language)
- **HuggingFace API** (`Qwen/Qwen2.5-72B-Instruct` via `langchain-huggingface`)
- **LangSmith** (Tracing and Debugging)
- **Rich** (Terminal UI formatting)

## Project Structure
```text
📦 TASK
 ┣ 📂 chains/              # Contains LCEL execution chains
 ┃ ┗ 📜 resume_chain.py
 ┣ 📂 data/                # Output directory for evaluation results
 ┃ ┣ 📜 results.json
 ┃ ┗ 📜 results.txt
 ┣ 📂 prompts/             # Contains LangChain PromptTemplates
 ┃ ┗ 📜 prompts.py
 ┣ 📜 main.py              # Main execution script
 ┣ 📜 requirements.txt     # Python dependencies
 ┣ 📜 .env.example         # Template for environment variables
 ┗ 📜 README.md            # Project documentation
```

## Setup & Installation

**1. Create a virtual environment**
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure Environment Variables**
Copy the `.env.example` file and rename it to `.env`. Fill in your API keys:
- Get your [Hugging Face Access Token](https://huggingface.co/settings/tokens).
- Get your [LangSmith API Key](https://smith.langchain.com/).

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=resume-screening-demo

HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_token_here
```

## Usage

Run the main pipeline to process the sample candidates (Strong, Average, Weak):

```bash
python main.py
```

### Viewing Traces
Navigate to your [LangSmith Dashboard](https://smith.langchain.com/) and open the `resume-screening-demo` project. You can inspect all prompt inputs, JSON outputs, parsed scores, latency, and tags for every candidate processed.

## Bonus Requirements Implemented
- ✅ **Few-Shot Prompting:** The `score_prompt` explicitly contains examples of graded scenarios to ground the LLM's grading baseline.
- ✅ **Structured JSON Output:** `JsonOutputParser` is utilized to strictly map outputs into dictionary structures to prevent text parsing errors.
- ✅ **LangSmith Tags:** Every `.invoke()` call pushes specific categorization tags to LangSmith to make filtering easier.