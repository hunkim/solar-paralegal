import requests
import json
import os


# Replace YOUR_API_KEY with your own Upstage API key
SOLAR_API_URL = os.getenv(
    "SOLAR_API_URL", "https://api.upstage.ai/v1/solar/chat/completions"
)

SYSTEM_INSTRUCTION = """You are Slack Follow-Up App. You are loved and appreciated.
You will get context and instruction from the user and you will provide the response based on the instruction.
Read instruction and context carefully and provide the response accordingly.
Response in the laangues of the context. 
For example, if the context is in English, MUST response in English.
If the context is in Korean, MUST response in Korean.
"""

class Solar:
    def __init__(self, endpoint=SOLAR_API_URL, api_key=os.getenv("SOLAR_API_KEY")):
        if not api_key:
            raise ValueError(
                "API key is required. Please set the SOLAR_API_KEY environment variable or pass it as an argument."
            )

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        self.endpoint = endpoint
        self.messages = []


    def set_messages(self, messages):
        self.messages = messages

    def invoke(
        self, messages=None, instruction="", model="solar-1-mini-chat", **options
    ):
        if not messages:
            messages = self.messages

        if not messages:
            messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
        elif messages[0].get("role") == "system":
            messages[0]["content"] = SYSTEM_INSTRUCTION
        else:
            messages.insert(0, {"role": "system", "content": SYSTEM_INSTRUCTION})
            
        if instruction:
            if messages[-1].get("role") == "user":
                messages[-1]["content"] = instruction
            else:
                messages.append({"role": "user", "content": instruction})

        context = {
            "model": model,
            "messages": messages,
            **options,
        }

        data = json.dumps(context, indent=2)
        # print(data)

        try:
            response = requests.post(self.endpoint, headers=self.headers, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def parse_response(response):
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")


if __name__ == "__main__":
    # Define the conversation context
    messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {
            "role": "assistant",
            "content": "I'm doing well, thank you! How can I help you today?",
        },
        {"role": "user", "content": "I have a question about solar energy."},
    ]

    # Create a Solar instance
    solar = Solar()
    solar_response = solar.invoke(messages=messages, instruction="Summarize the given text in a polite manner")
    response_text = Solar.parse_response(solar_response)
    print(response_text)
