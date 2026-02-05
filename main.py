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

url = "https://leetcode-api-pied.vercel.app/problems"

def insert_single_question(question_data):
    """Insert a single question into Supabase"""
    try:
        # Transform the data to match your table structure
        row_data = {
            "question_id": question_data.get("questionId"),
            "question_frontend_id": question_data.get("questionFrontendId"),
            "title": question_data.get("title"),
            "content": question_data.get("content"),
            "likes": question_data.get("likes", 0),
            "dislikes": question_data.get("dislikes", 0),
            "stats": json.loads(question_data.get("stats", "{}")) if isinstance(question_data.get("stats"), str) else question_data.get("stats"),
            "similar_questions": json.loads(question_data.get("similarQuestions", "[]")) if isinstance(question_data.get("similarQuestions"), str) else question_data.get("similarQuestions"),
            "category_title": question_data.get("categoryTitle"),
            "hints": question_data.get("hints", []),
            "topic_tags": question_data.get("topicTags", []),
            "company_tags": question_data.get("companyTags"),
            "difficulty": question_data.get("difficulty"),
            "is_paid_only": question_data.get("isPaidOnly", False),
            "solution": question_data.get("solution"),
            "has_solution": question_data.get("hasSolution", False),
            "has_video_solution": question_data.get("hasVideoSolution", False),
            "url": question_data.get("url")
        }
        
        # Insert into Supabase
        response = supabase.table("leetcode_questions").insert(row_data).execute()
        print(f"✓ Inserted question {row_data['question_id']}: {row_data['title']}")
        return response
    except Exception as e:
        print(f"✗ Error inserting question {question_data.get('questionId')}: {str(e)}")
        return None

#Phase 1: Get data from API and save to JSON file
try:
    response = requests.get(url)
    data = response.json()
    
    with open('problems.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)    
    
    print(f"{len(data)} Problems saved to problems.json")
    
except Exception as e:
    print(f"Error fetching data: {e}")
    exit(1)


# Phase 2: Load data from JSON file and store in csv to uploaded to the database
with open('problems.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    df = pandas.DataFrame(data)
    df = df[['id', 'title', 'title_slug', 'url']]
    df.to_csv('problems.csv', index=False)
    print(f"{len(df)} Problems saved to problems.csv")

    
# Phase 3: Updating the problems information to avoid content copy writing
with open('problems.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    for problem in data:
        problem = dict(problem)
        problem_url = f"https://leetcode-api-pied.vercel.app/problem/{problem['title_slug']}"
        try:
            response = requests.get(problem_url)
            data = response.json()
            print(f"Fetched data for url: {problem['url']}")
            insert_single_question(data)
        except Exception as e:
            print(f"Error fetching url: {problem['url']}")
            continue
        
    
