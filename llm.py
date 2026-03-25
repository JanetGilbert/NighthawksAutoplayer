import json
import os
import random
import re
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

if LLM_PROVIDER == "huggingface":
    HF_API_KEY = os.environ["HUGGINGFACE_API_KEY"]
    HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
    MODEL = os.getenv("HUGGINGFACE_INFERENCE", "Qwen/Qwen2.5-72B-Instruct")
else:
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )
    MODEL = os.getenv("OLLAMA_MODEL", "phi4-mini")

with open("system_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

choice_history: list[str] = []


def decide(data, choices: list) -> int:
    max_retries = 5
    data["history"] = choice_history
    print(json.dumps(data, indent=2))
    
    for attempt in range(max_retries):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(data)},
        ]

        if LLM_PROVIDER == "huggingface":
            resp = requests.post(
                HF_CHAT_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {HF_API_KEY}",
                },
                json={"model": MODEL, "messages": messages, "max_tokens": 2048},
            )
            print(f"HF API status: {resp.status_code}")
            print(f"HF API full response: {resp.text}")
            resp_json = resp.json()
            if resp.status_code != 200:
                print(f"ERROR: HF API error: {resp_json}")
                continue
            raw = resp_json["choices"][0]["message"]["content"]
        else:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=512,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content

        print(f"LLM raw response (attempt {attempt + 1}): {raw}")

        # Strip <think>...</think> tags (Qwen3.5 thinking mode)
        if raw:
            raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

        if not raw:
            print(f"ERROR: LLM returned empty response")
            continue

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            print(f"ERROR: LLM response is not valid JSON: {raw}")
            continue

        if "choice" not in result:
            print(f"ERROR: LLM response missing 'choice', got: {result}")
            continue

        choice = result["choice"]
        justification = result.get("justification", "")


        print(f"LLM chose {choice}")
        print(f"Justification: {justification}")
        _record_choice(choice)
        return choice, justification

    print(f"ERROR: LLM failed after {max_retries} attempts, picking randomly")
    choice = random.choice(choices)
    _record_choice(choice)
    return choice, "Random override - LLM failed to return valid option"


def _record_choice(choice_text: str):
    choice_history.append(choice_text)
    if len(choice_history) > 30:
        del choice_history[:-30]
