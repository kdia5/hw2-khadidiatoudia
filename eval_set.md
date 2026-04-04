Evaluation Set: Research & Journal Helper
1. Normal Case: FDA Device Fact (Secondary Project)
Input: "The Kardiaband is a wearable for the Apple Watch. It uses ECG sensors. The study size was 51 people."
Good Output Should: List the Device, Sensor Type, and Study Size in a clear list.

2. Normal Case: Lab Meeting Notes (Primary Project)
Input: "Met with Yu and Yichen. We discussed the PPG sensor project. Yu needs to finish the data cleaning by Friday."
Good Output Should: List the People Involved, the Sensor discussed, and the "To-Do" item with its deadline.

3. Normal Case: Writing Tasks
Input: "The journal article needs a section on FDA trends. I have found 950+ devices so far. We should mention that most are for radiology."
Good Output Should: Summarize this as a "Writing Goal" and include the data point about the number of devices.

4. Edge Case: Very Messy Notes
Input: "Sensor? maybe PPG. ask Weiguang. check Kardiaband again. 2026 deadline."
Good Output Should: Group these as "Uncertain Items" or "Questions to Ask" instead of pretending the information is complete.

5. Failure/Hallucination Case: Missing Info (Likely to Fail)
Input: "I am reading a paper about a new sensor. It doesn't say who the author is or what the accuracy was. Please write a summary anyway."
Good Output Should: State that it cannot provide a summary of the author or accuracy because that information is missing. Note: The AI will likely fail by making up a fake author name or a fake accuracy percentage.
