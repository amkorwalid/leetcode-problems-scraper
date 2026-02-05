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

response = supabase.table("leetcode_questions").select("*").execute()

data = response.data[:3]
for row in data:
    print(row["question_id"], row["title"])