import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def review_diff_with_gpt4(diff: str) -> str:
    prompt = f"""
You are an expert code reviewer. Given the following git diff, provide:
1. A concise summary of the changes.
2. Inline review comments with file and line context (eg. `filepy:40`).
3. General Suggestion for Improvemnet.

Diff: 
{diff}
"""  
    resp = client.chat.completions.create(
        model = "gpt-4",
        messages = [
            {"role": "system", "content": "You are a helpful, detail-oriented code reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens = 1500,
    )
    return resp.choices[0].message.content

