from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
import json
import base64
import os

app = FastAPI()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

class FileReview(BaseModel):
    file: str
    content: str
    diff: str

class ReviewRequest(BaseModel):
    files: List[FileReview]

@app.post("/review")
def review_code(req: ReviewRequest):
    all_reviews = []

    for f in req.files:
        try:
            content = base64.b64decode(f.content).decode("utf-8")
            diff = base64.b64decode(f.diff).decode("utf-8")
        except Exception as e:
            continue

        prompt = f"""
You are an expert AI code reviewer.

Here is the full file content of `{f.file}`:
```python
{content}
```

And here is the Git diff:
```diff
{diff}
```

Please suggest improvements based on both the diff and the full context.
Return a JSON response like this:
{{
  "review": [
    {{
      "file": "file.py",
      "line": 42,
      "comment": "Detailed comment"
    }}
  ],
  "summary": "Overall review summary",
  "severity": "minor"
}}

Respond ONLY with valid JSON.
"""

        try:
            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": "codellama",
                "prompt": prompt,
                "stream": False
            })
        except Exception as e:
            continue

        raw_output = response.json().get("response", "")

        try:
            start = raw_output.find("{")
            end = raw_output.rfind("}") + 1
            json_str = raw_output[start:end]
            parsed = json.loads(json_str)
            all_reviews.append(parsed)
        except Exception:
            all_reviews.append({
                "review": [],
                "summary": "⚠️ Could not parse output for file: " + f.file,
                "severity": "critical",
                "raw_output": raw_output
            })

    return {"reviews": all_reviews}
