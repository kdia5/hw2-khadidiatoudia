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


def format_api_error(exc: urllib.error.HTTPError) -> str:
    details_text = exc.read().decode("utf-8", errors="replace")

    try:
        details = json.loads(details_text)
    except json.JSONDecodeError:
        return f"Gemini API request failed with HTTP {exc.code}: {details_text}"

    error = details.get("error", {})
    message = error.get("message", "Unknown API error.")
    status = error.get("status", "")

    if exc.code == 429 or status == "RESOURCE_EXHAUSTED":
        return textwrap.dedent(
            f"""
            Gemini API quota error:
            {message}

            This is not a Python bug in your script. Your API key/project
            currently has no available Gemini quota or billing for this model.

            What to do:
            1. Open Google AI Studio or Google Cloud billing/quota settings.
            2. Make sure the API key belongs to a project with Gemini API access.
            3. Enable billing or wait for quota reset if you are on the free tier.
            4. Then rerun `python3 app.py`.
            """
        ).strip()

    if exc.code == 404 or status == "NOT_FOUND":
        return textwrap.dedent(
            f"""
            Gemini model error:
            {message}

            The model name is not available for your API/project.
            Try setting another model, for example:
            `export GEMINI_MODEL='gemini-2.0-flash'`
            or
            `export GEMINI_MODEL='gemini-1.5-flash'`
            """
        ).strip()

    return f"Gemini API request failed with HTTP {exc.code}: {message}"


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
        raise RuntimeError(format_api_error(exc)) from exc
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
        help="Raw notes to summarize.",
    )
    parser.add_argument(
        "--notes",
        help="Alias for --input, kept for compatibility with your earlier commands.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model name. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--output",
        help="Optional file path to save the output.",
    )
    return parser.parse_args()


def get_notes(args: argparse.Namespace) -> str:
    notes = args.input or args.notes
    if notes:
        return notes

    if not sys.stdin.isatty():
        return sys.stdin.read()

    print("Paste your research notes below, then press Enter:")
    return input("> ").strip()


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Missing GEMINI_API_KEY. Run: export GEMINI_API_KEY='your_api_key_here'",
            file=sys.stderr,
        )
        return 1

    notes = get_notes(args)
    if not notes.strip():
        print("No notes were provided.", file=sys.stderr)
        return 1

    try:
        result = call_gemini(notes=notes, api_key=api_key, model=args.model)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(result)
        print(f"Saved structured notes to {args.output}")
    else:
        print("\n--- Structured Research Notes ---\n")
        print(result)
        print("\n---------------------------------")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
