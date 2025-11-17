
# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json

class ActionQueryLlama(Action):
    def name(self):
        return "action_query_llama"

    def run(self, dispatcher, tracker, domain):
        user_message = tracker.latest_message.get("text")

        # Call your LLaMA server API
        try:
            response = requests.post(
                    "http://localhost:11434/api/generate",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "llama3",
                    "prompt": user_message
                },
                timeout=30
            )

            # Split the response into lines and parse each JSON object
            answers = []
            for line in response.text.splitlines():
                if line.strip():  # skip empty lines
                    try:
                        obj = json.loads(line)
                        if "response" in obj and obj["response"]:
                            answers.append(obj["response"])
                    except json.JSONDecodeError:
                        # ignore lines that are not valid JSON
                        pass

            # Join all partial responses
            final_answer = "".join(answers) if answers else "No response from LLaMA."
            dispatcher.utter_message(text=final_answer)

        except Exception as e:
            dispatcher.utter_message(text=f"Failed to connect to LLaMA API: {e}")


        return []
