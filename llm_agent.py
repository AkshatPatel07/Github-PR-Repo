import os
from huggingface_hub import InferenceClient
import requests
from dotenv import load_dotenv

load_dotenv()

token=os.getenv("HF_API_TOKEN"),

client = InferenceClient(
    model="mistralai/Mistral-7B-v0.1",
    token=token,
    timeout=120,
)

def review_diff_with_hf(diff: str) -> str:
    system_prompt = (
        "SYSTEM: You are an expert software engineer reviewing a GitHub pull request.\n"
        "Analyze this diff and provide:\n"
        "1. A concise summary of changes\n"
        "2. Actionable comments with file:line references\n"
        "3. Security and code-quality suggestions\n\n"
        "USER: Here is the diff:\n"
        f"{diff}\n\n"
        "ASSISTANT:"
    )
    
    try:
        result = client.text_generation(
            system_prompt,
            max_new_tokens=1024,
            temperature=0.1
        )
        # result is a list of GeneratedText
        return result[0].generated_text.strip()

    except Exception as e:
        return f"Error generating review: {e}"



