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


def decide(scenario: str, dialog: list, choices: list) -> int:
    user_message = f"""Scenario: {scenario}

Dialog: {json.dumps(dialog)}

ChoiceMaximum: {len(choices) - 1}

Choices:
{chr(10).join(f"index {i}: {c}" for i, c in enumerate(choices))}"""
    
    print(user_message)

    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    result = json.loads(response.choices[0].message.content)
    index = int(result["index"])
    justification = result.get("justification", "")

    if index < 0 or index >= len(choices):
        print(f"ERROR: LLM returned out-of-range index {index} (valid: 0-{len(choices)-1}), defaulting to 0")
        index = random.randint(0, len(choices)-1)
        justification="Random override"

    print(f"LLM chose index {index}: {choices[index]}")
    print(f"Justification: {justification}")
    return index, justification
