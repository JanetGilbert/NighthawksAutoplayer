# NighthawksAutoplayer

## Purpose
A local Python server that acts as an automatic game player for **Nighthawks**, a Godot visual novel. The server receives game state from the Godot client and will eventually make decisions about which button to click, simulating a player.

## How it fits together
- **Nighthawks** is a Godot project (separate repo, not in this directory)
- The Godot game uses `HTTPRequest` to POST to this server and awaits a response
- The server runs locally at `http://127.0.0.1:8080`
- Interaction is turn-based: the game sends text, the server decides what to do next

## API

### `POST /decide`
The only endpoint. Called by the Godot game each turn.

**Request body:**
```json
{
  "scenario": "Narrative text describing the current scene",
  "dialog": [],
  "choices": ["Choice A", "Choice B", "Choice C"]
}
```

**Response (choices available):**
```json
{ "pick": 2 }
```
`pick` is the chosen option.

**Response (no choices):**
Logs an error to the console and returns:
```json
{ "status": "error", "message": "no choices" }
```

## Choice memory
- The server keeps an in-memory list of the last 30 choices (by text, not index)
- This history is included in the LLM prompt so it favors unexplored options
- History resets on server restart
- Single-choice turns (handled before calling the LLM) are not recorded

## Project structure
```
server.py           # Flask server, entry point
llm.py              # LLM integration (Ollama / qwen3:8b via OpenAI-compatible API)
system_prompt.txt   # LLM system prompt (loaded at startup)
requirements.txt    # Python dependencies
```

## Running the server
```bash
pip install -r requirements.txt
python server.py
```

## Development notes
- Built incrementally prompt by prompt — keep this file up to date
- Python with Flask; no database, no auth
- This is a local-only tool, never exposed to the internet

---

## Instructions for Claude
**Update this file after every significant change.** Significant changes include:
- New or modified API endpoints (update the API section)
- New dependencies added to requirements.txt
- New files or modules added (update project structure)
- Changes to how the Godot client and server communicate
- Any new development patterns or conventions established
