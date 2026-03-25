import json
import random
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client but unused by Ollama
)

#MODEL = "qwen3:8b"
MODEL = "phi4-mini"

with open("system_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

choice_history: list[str] = []


def decide(data, choices: list) -> int:
    max_retries = 5
    data["history"] = choice_history
    print(json.dumps(data, indent=2))
    
    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(data)},
            ],
        )

        raw = response.choices[0].message.content
        print(f"LLM raw response (attempt {attempt + 1}): {raw}")
        result = json.loads(raw)

        if "index" not in result:
            print(f"ERROR: LLM response missing 'index' key, got: {result}")
            continue

        index = int(result["index"])
        justification = result.get("justification", "")

        if index < 0 or index >= len(choices):
            print(f"ERROR: LLM returned out-of-range index {index} (valid: 0-{len(choices)-1})")
            continue

        print(f"LLM chose index {index}: {choices[index]}")
        print(f"Justification: {justification}")
        _record_choice(choices[index])
        return index, justification

    print(f"ERROR: LLM failed after {max_retries} attempts, picking randomly")
    index = random.randint(0, len(choices) - 1)
    _record_choice(choices[index])
    return index, "Random override - LLM failed to return valid index"


def _record_choice(choice_text: str):
    choice_history.append(choice_text)
    if len(choice_history) > 30:
        del choice_history[:-30]
