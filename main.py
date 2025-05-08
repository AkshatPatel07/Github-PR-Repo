from fastapi import FastAPI, Request, HTTPException
import os
from dotenv import load_dotenv
from app.github import init_github_client, get_pr_diff

load_dotenv()

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
client = init_github_client(GITHUB_TOKEN)


@app.post('/webhook')
async def github_wehook(requests: Request):
    try:
        event = requests.headers.get("X-Github-Event")
        if event != "pull_request":
            return {"message": "Ignoring non-PR event"}
        
        payload = await requests.json()
        action = payload.get("action")

        if action not in ["opened", "synchronize", "reopened"]:
            return {"message": f"Ignoring actions: {action}"}

        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        pr_url = pr.get("url")
        pr_title = pr.get("title")
        pr_user = pr.get("user", {}).get("login")

        repo = payload.get("repository", {})
        repo_full_name = repo.get("full_name")

        print(f"📦 Received PR from {pr_user}: {pr_title} ({pr_url})")

        title, diff = get_pr_diff(client, repo_full_name, pr_number)

        print(f"🔍 PR Title: {title}")
        print(f"📝 PR Diff:\n{diff[:500]}...")  
        
        return {"message": "PR event processed and diff fetched"}
    
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Invalid Payload")
    