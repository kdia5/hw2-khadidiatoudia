import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# For OpenRouter, we can use free models like 'meta-llama/llama-3-8b-instruct:free'
DEFAULT_MODEL = "openrouter/free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter(notes, api_key, instruction, model):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": f"Please structure these research notes:\n\n{notes}"}
        ],
        "temperature": 0.3
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter
        "X-Title": "JHU Research Assistant Pro"
    }

    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data['choices'][0]['message']['content'].strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return f"API Error {e.code}: {error_body}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def main():
    parser = argparse.ArgumentParser(description="Research Note Structuring Tool (OpenRouter Version)")
    parser.add_argument("--notes", required=True, help="The raw notes to process.")
    parser.add_argument("--instruction", 
                        default="You are a professional research assistant. Format these notes into: Key Takeaways, Methodology, and Action Items.",
                        help="Custom system instructions.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use (default is free llama-3).")
    
    args = parser.parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not found.")
        return 1

    print(f"Processing with {args.model} via OpenRouter...")
    result = call_openrouter(args.notes, api_key, args.instruction, args.model)
    
    print("\n--- Structured Output ---\n")
    print(result)
    print("\n--------------------------")
    return 0

if __name__ == "__main__":
    sys.exit(main())
