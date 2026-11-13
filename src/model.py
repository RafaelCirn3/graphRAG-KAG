import json
import urllib.request
from src.config import settings


def ask(system, prompt, structured=False):
    payload = {"model": settings.llm_model, "stream": False,
               "options": {"temperature": 0}, "messages": [
                   {"role": "system", "content": system}, {"role": "user", "content": prompt}]}
    if structured:
        payload["format"] = structured if isinstance(structured, dict) else "json"
    request = urllib.request.Request(settings.ollama_url + "/api/chat",
                                     data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=180) as response:
        answer = json.load(response)["message"]["content"]
    return json.loads(answer) if structured else answer

