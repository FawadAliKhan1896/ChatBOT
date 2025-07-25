from googlesearch import search
from groq import Groq
from json import load, dump
from dotenv import dotenv_values
import datetime

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
AssistantName = env_vars.get("AssistantName")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

CHATLOG_PATH = "data/Chatlog.json"

try:
    with open(CHATLOG_PATH, "r") as f:
        messages = load(f)
except:
    with open(CHATLOG_PATH, "w") as f:
        dump([], f)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

def AnsweModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you today?"}
]

def Information():
    now = datetime.datetime.now()
    return (
        "Please use this real-time information if needed:\n\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Hour: {now.strftime('%I')}\n"
        f"Minute: {now.strftime('%M')}\n"
        f"Second: {now.strftime('%S')}\n"
        f"AM/PM: {now.strftime('%p')}\n\n"
    )

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    with open(CHATLOG_PATH, "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})
    SystemChatBot.append({"role": "user", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        max_tokens=1024,
        temperature=0.7,
        top_p=1,
        stream=True
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(CHATLOG_PATH, "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnsweModifier(Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
