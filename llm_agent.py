import os
from huggingface_hub import InferenceClient
import requests
from dotenv import load_dotenv

load_dotenv()


client = InferenceClient(
    token=os.getenv("HF_API_TOKEN"),
    model="meta-llama/Llama-3-8b-instruct",
    timeout=120,  # Longer timeout for bigger model
)


def review_diff_with_hf(diff: str) -> str:
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert software engineer reviewing a GitHub pull request.
    Analyze this diff and provide:
    1. A concise summary of changes
    2. Specific, actionable feedback with file:line references
    3. Security/code quality suggestions
    Format using Markdown<|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Diff:
    {diff}<|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>"""
    
    try:
        # Single-positional-arg interface: prompt first, then generation kwargs
        result = client.text_generation(
            prompt,
            max_new_tokens=1024,
            temperature=0.1,
            repetition_penalty=1.2,
        )
        # `result` is a list of GeneratedText objects
        return result[0].generated_text.strip()

    except Exception as e:
        return f"Error generating review: {e}"



