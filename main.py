from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from app.llm_agent import review_diff_with_gpt4
from app.review_parser import parse_review_comments
from app.github import post_review_comments
import os
from dotenv import load_dotenv
from app.github import init_github_client, get_pr_diff

load_dotenv()
app = FastAPI()

client = init_github_client(os.getenv("GITHUB_TOKEN"))

def process_pr(repo_full_name: str, pr_number: int):
    # Fetches Diff
    title, diff = get_pr_diff(client, repo_full_name, pr_number)

    # Gets raw review text from GPT
    review_text = review_diff_with_gpt4(diff)

    # Parse that into structured comments
    comments, summary = parse_review_comments(review_text)

    # Post back to Github
    post_review_comments(client, repo_full_name, pr_number, comments, summary)

    print(f"[BG] PR #{pr_number} Title: {title}")
    print(f"[BG] Diff preview:\n{diff[:200]}…")

    try:
        review = review_diff_with_gpt4(diff)
        print(f"[BG] 🤖 AI Review for PR #{pr_number}:\n{review}")
    except Exception as e:
        print(f"[BG] Error calling LLM: {e}")

@app.get("/ping")
async def ping():
    return {"pong": True}

@app.post('/webhook')
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    print("➡️ Entered /webhook handler")   

    try:
        event = request.headers.get("X-GitHub-Event")
        print(f"Github Event: {event}")

        if event != "pull_request":
            return {"message": "ignoring non PR event"}

        body = await request.json()
        action = body.get("action")
        print(f"PR Action: {action}")

        if action not in ["opened", "synchronize", "reopened"]:
            return {"msg": "ignored"}

        pr   = body.get("pull_request", {})
        pr_number = pr.get("number")
        pr_title = pr.get("title")
        pr_user = pr.get("user", {}).get("login")
        pr_url = pr.get("url")

        repo = body.get("repository", {})
        repo_full_name = repo.get("full_name")

        print(f"Recieved PR from {pr_user}: {pr_title} ({pr_url})")

        title, diff = get_pr_diff(client, repo_full_name, pr_number)
        print(f"PR Title: {title}")
        print(f"PR Diff: \n{diff[:500]}...")    

        background_tasks.add_task(process_pr, repo_full_name, pr_number)

    
    except Exception as e:
        print(f"Error Handling webHook: {e}")
        raise HTTPException (status_code=400, detail="Invalid Payload")
