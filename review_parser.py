import re

def parse_review_comments(review_text: str) -> tuple[list[dict], str]:
    """
    Parses GPT-4 review into:
    comments: a list od dict with keys 'path', 'line', 'body'
    summary: a string with overall feedback
    """

    comments = []
    summary = ""
    lines = review_text.splitlines()
    comment_pattern = re.compile(r"^(.+\.py):(\d+)\s*-\s*(.+)$")

    for line in lines:
        m = comment_pattern.match(line)
        if m:
            path, line_no, msg = m.groups()
            comments.append({"path": path, "line": int(line_no), "body": msg})
        else:
            summary += line + "\n"
    
    return comments, summary.strip()
