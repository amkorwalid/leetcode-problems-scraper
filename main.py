import requests
import json
import pandas
import os
from openai import OpenAI
from insert_row import insert_single_question



url = "https://leetcode-api-pied.vercel.app/problems"

# Phase 1: Get data from API and save to JSON file
# try:
#     response = requests.get(url)
#     data = response.json()
    
#     with open('problems.json', 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4, ensure_ascii=False)    
    
#     print(f"{len(data)} Problems saved to problems.json")
    
# except Exception as e:
#     print(f"Error fetching data: {e}")
#     exit(1)


# Phase 2: Load data from JSON file and store in csv to uploaded to the database
# with open('problems.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)
#     df = pandas.DataFrame(data)
#     df = df[['id', 'title', 'title_slug', 'url']]
#     df.to_csv('problems.csv', index=False)
#     print(f"{len(df)} Problems saved to problems.csv")

    
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
        
    
