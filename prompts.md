Prompt Iteration Record:

Initial Version
System Instruction: "You are a professional research assistant. Format these notes into: Key Takeaways, Methodology, and Action Items."
What changed and why: This was the baseline prompt designed to test if the model could handle basic formatting and sectioning for rough, messy lab notes. 
What improved/worsened: The model successfully applied the headers, but it forced vague fragments into rigid categories. For example, it turned a simple note to "ask Weiguang" into formal "Methodology" and "Action Item" steps, artificially over-structuring the messy input.

Revision 1
System Instruction: "You are a professional research assistant. Format these notes into: Key Takeaways, Methodology, and Action Items. If any notes are unclear, group them into 'Uncertain Items/Questions'."
What changed and why: Added a specific bucket for unclear items to handle edge cases, testing it against a "Missing Info" scenario.
What improved/worsened: The model successfully avoided hallucinating fake data, simply stating "No specific methodology information provided." However, the response was somewhat passive and didn't clearly flag the severity of the missing data for the research team.

Revision 2 (Final)
System Instruction: "You are a professional research assistant. Format these notes into: Key Takeaways, Methodology, and Action Items. If any notes are unclear, group them into 'Uncertain Items/Questions'. CRITICAL: If important details are missing, explicitly state 'Information Missing'. Do not invent facts."
What changed and why: Added a strict anti-hallucination guardrail to force the model to explicitly flag missing critical details rather than just passively leaving sections blank.
What improved/worsened: This was the most effective version. The model explicitly printed "Information Missing:" under the empty headers. It also utilized the "Uncertain Items/Questions" section to generate highly relevant follow-up questions (ex: "What specific aspects... were deemed 'good'?") to help guide the researcher in filling the gaps.
