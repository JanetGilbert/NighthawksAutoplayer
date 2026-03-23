import json
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client but unused by Ollama
)

MODEL = "qwen3:8b"

SYSTEM_PROMPT = """You are playing a vampire visual novel called Nighthawks.
You will be given the current scenario, any recent dialog, and a list of choices.
Respond with a JSON object in this exact format: {"index": <number>, "justification": "<reasoning>"}
where <number> is the zero-based index of the choice you want to make,
and <reasoning> is a brief explanation of why you made that choice.
Do not include any other text or explanation."""


def decide(scenario: str, dialog: list, choices: list) -> int:
    user_message = f"""Scenario: {scenario}

Dialog: {json.dumps(dialog)}

Choices:
{chr(10).join(f"{i}: {c}" for i, c in enumerate(choices))}"""

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
    print(f"LLM chose index {index}: {choices[index]}")
    print(f"Justification: {justification}")
    return index, justification
