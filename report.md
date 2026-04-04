Step 4 Report

Model used:
- Gemini via the Google Generative Language API
- Default app setting: gemini-2.0-flash

What I built:

- A small Python CLI in `app.py`
- The script reads `GEMINI_API_KEY` from the environment
- It sends rough research notes to Gemini and returns a structured summary
- The prompt is designed to avoid hallucination and to separate uncertain facts from confirmed ones

Evaluation summary:

1. FDA device fact case
- Expected result: extract device, sensor type, and study size clearly
- Likely outcome: should pass because the input is short and fact-based

2. Lab meeting notes case
- Expected result: identify people, project topic, and to-do item
- Likely outcome: should pass because the notes are explicit and well-scoped

3. Writing task case
- Expected result: summarize the writing goal and preserve the 950+ device count
- Likely outcome: should pass because the data point is directly stated

4. Messy notes edge case
- Expected result: move incomplete information into "Questions to Ask" or "Uncertain Items"
- Likely outcome: should mostly pass because the prompt explicitly tells the model not to treat uncertain details as confirmed facts

5. Missing-information failure case
- Expected result: refuse to invent the author or accuracy value
- Main risk: the model may still try to over-complete the summary if the prompt is not strict enough
- Mitigation used: the system prompt explicitly says to state that key details are missing instead of guessing

Main lesson:

The most important part of this workflow is not just summarization. It is making the model handle incomplete notes safely. A strong prompt helps the model organize messy research notes while reducing the chance that it fabricates missing details.

How to run:

`export GEMINI_API_KEY='your_key_here'`

`python3 app.py --input "Met with Yu and Yichen. We discussed the PPG sensor project. Yu needs to finish the data cleaning by Friday."`
