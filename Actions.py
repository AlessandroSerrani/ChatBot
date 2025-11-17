from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import json
import time

# SSE server endpoint
SSE_PUSH_URL = "http://127.0.0.1:5006/push"

class ActionQueryLlama(Action):
    def name(self):
        return "action_query_llama"

    def run(self, dispatcher, tracker, domain):
        user_message = tracker.latest_message.get("text")

        try:
            # Call Ollama with streaming enabled
            response = requests.post(
                "http://localhost:11434/api/generate",
                headers={"Content-Type": "application/json"},
                json={"model": "llama3", "prompt": user_message},
                timeout=30,
                stream=True  # Important: stream response line by line
            )

            # Read lines as Ollama produces them
            for line in response.iter_lines(decode_unicode=True):
                if not line.strip():
                    continue

                try:
                    obj = json.loads(line)
                    token = obj.get("response", "")
                    if not token:
                        continue

                    # Push each token immediately to SSE
                    requests.post(SSE_PUSH_URL, json={"token": token}, timeout=0.5)

                    # Optional: small delay to create smooth typing effect
                    time.sleep(0.01)

                except json.JSONDecodeError:
                    continue

            # Optional: send empty final message via dispatcher
            dispatcher.utter_message(text="")

        except Exception as e:
            dispatcher.utter_message(text=f"Error contacting LLaMA: {e}")

        return []

