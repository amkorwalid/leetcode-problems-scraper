import requests
import json
import pandas
import os
from openai import OpenAI
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

def insert_cleaned_problem(problem_data):
    """Insert a single problem pattern into Supabase"""
    if isinstance(problem_data, str):
        problem_data = json.loads(problem_data)
    try:
        row_data = {
            "id": problem_data.get("id"),
            "title": problem_data.get("title"),
            "difficulty": problem_data.get("difficulty"),
            "topics": problem_data.get("topics", []),
            "problem_summary": problem_data.get("problem_summary"),
            "canonical_idea": problem_data.get("canonical_idea"),
            "quiz": problem_data.get("quiz"),
            "key_insight": problem_data.get("key_insight"),
            "pseudo_code": problem_data.get("pseudo_code", []),
            "common_traps": problem_data.get("common_traps", [])
        }
        
        response = supabase.table("genai_problems").insert(row_data).execute()
        print(f"Inserted problem {row_data['id']}: {row_data['title']}")
        return response
    except Exception as e:
        print(f"Error inserting problem {problem_data.get('id')}: {str(e)}")
        return None

client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

system_prompt = """ 
You are a LeetCode-to-Quiz converter. Transform LeetCode problems into structured JSON for quiz preparation.

**INPUT FORMAT:**
- Problem description (title, difficulty, examples, constraints)
- One or more solution approaches with explanations
- Common pitfalls

**OUTPUT FORMAT:** Pure JSON only, no explanations, following this exact schema:

{
    "id": X, (integer extract from the input or generate)
    "title": "Problem Title",
    "difficulty": "easy/medium/hard",
    "topics": ["topic1", "topic2", ...], (from tags or inferred)
    "problem_summary": "1-2 sentence description",
    "canonical_idea": {
        "pattern": "primary_algorithmic_pattern",
        "one_liner": "brief optimal solution description"
    },
    "quiz": {
        "question": "Multiple choice question testing key concept",
        "options": [
        {
            "id": "A",
            "text": "Option text",
            "is_correct": true/false,
            "why_wrong": "explanation if incorrect",
            "tags": ["tag1", "tag2"]
        }
        ] (include exactly 4 options)
    },
    "key_insight": "The crucial realization for solving",
    "pseudo_code": ["line1", "line2", ...], (5-8 lines max)
    "common_traps": ["trap1", "trap2", "trap3"]
}

**RULES:**
1. Extract "canonical_idea" from the most efficient/common solution
2. Quiz question should test understanding of optimal approach
3. Make incorrect options plausible but clearly wrong
4. Pseudo-code should show core logic, not full implementation
5. Base topics on problem tags when available
6. Keep all content concise and instructional
7. Output ONLY the JSON, no markdown, no extra text

**Now transform the next problem.**


"""

response = supabase.table("leetcode_questions").select("*").execute()

data = response.data[:3]
for row in data:
    user_prompt = f"""
        id {row['question_id']}, title {row['title']}, 
        {row['content']} 
        {row['url']} 
        {row['stats']}
        {row['category_title']}
        {row['difficulty']}
        {row['hints']}
        {row['topic_tags']}
        {row['solution']}
        {row['solution']}
    """
    messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    
    insert_cleaned_problem(response.choices[0].message.content)