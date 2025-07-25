from groq import Groq
from json import loads, dumps
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
AssistantName = env_vars.get("AssistantName")
GroqAPIKey = env_vars.get("GroqAPIKey")  # corrected variable name

client = Groq(api_key=GroqAPIKey)

SystemPrompt = f"""
Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

systemChatBot = [{"role": "system", "content": SystemPrompt}]

# Load chat history
try:
    with open("Data/Chatlog.json", "r", encoding="utf-8") as f:
        messages = loads(f.read())
except FileNotFoundError:
    messages = []
    with open("Data/Chatlog.json", "w", encoding="utf-8") as f:
        dumps(messages, f)

# Real-time info
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed:\n\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Hour: {now.strftime('%I')}\n"
        f"Minute: {now.strftime('%M')}\n"
        f"Second: {now.strftime('%S')}\n"
        f"AM/PM: {now.strftime('%p')}\n\n"
    )

# Clean Answer Output
def AnswerModifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# Chat Function
def ChatBot(query):
    try:
        with open("Data/Chatlog.json", "r", encoding="utf-8") as f:
            messages = loads(f.read())

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=systemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        with open("Data/Chatlog.json", "w", encoding="utf-8") as f:
            f.write(dumps(messages, indent=4))

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."

# Run loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input))
