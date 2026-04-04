import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.request


DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a research workflow assistant that converts rough internal notes
    into a structured summary without inventing facts.

    Rules:
    1. Use only the information provided in the notes.
    2. If details are uncertain, place them under "Uncertain Items".
    3. If the notes contain questions or follow-ups, place them under
       "Questions to Ask" or "Action Items".
    4. If important details are missing, say they are missing instead of
       guessing.
    5. Keep the answer concise, organized, and easy for a research team to scan.

    Output format:
    - Title
    - Key Takeaways
    - Methodology / Context
    - Action Items
    - Questions to Ask
    - Uncertain Items

    If a section has no content, write "None noted."
    """
).strip()


def build_user_prompt(notes: str) -> str:
    return textwrap.dedent(
        f"""
        Convert the following rough research notes into a structured internal
        knowledge-base summary.

        Notes:
        {notes.strip()}
        """
    ).strip()


def call_gemini(notes: str, api_key: str, model: str) -> str:
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": build_user_prompt(notes)}]}],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.8,
            "maxOutputTokens": 700,
        },
    }

    request = urllib.request.Request(
        API_URL.format(model=model, api_key=api_key),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API request failed: {exc.code} {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach Gemini API: {exc.reason}") from exc

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"No candidates returned by Gemini API: {data}")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if "text" in part]
    if not text_parts:
        raise RuntimeError(f"No text content returned by Gemini API: {data}")
    return "\n".join(text_parts).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Turn rough research notes into a structured summary with Gemini."
    )
    parser.add_argument(
        "--input",
        help="Raw notes to summarize. If omitted, the app reads from stdin.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model name. Default: {DEFAULT_MODEL}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Missing GEMINI_API_KEY. Export your API key before running this script.",
            file=sys.stderr,
        )
        return 1

    notes = args.input if args.input else sys.stdin.read()
    if not notes.strip():
        print("Provide notes with --input or via stdin.", file=sys.stderr)
        return 1

    try:
        result = call_gemini(notes=notes, api_key=api_key, model=args.model)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
