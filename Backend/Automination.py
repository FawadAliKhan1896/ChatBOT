from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt as PlayYouTube
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import os
import requests
import keyboard
import asyncio

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")

# Ensure 'Data' directory exists
os.makedirs("Data", exist_ok=True)

# Groq client
client = Groq(api_key=GroqAPIKey)

# Classes for scraping
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb"]

# User agent for scraping
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.489.75 Safari/537.36'

# AI system prompt
SystemChatBot = [{
    "role": "system",
    "content": f"Hello I am {Username}. You are a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc. "
               f"You are a very accurate and advanced AI content writer. Write in a professional way using proper grammar, punctuation, and structure."
}]

# Stores chat messages
messages = []

# Professional responses
professional_responses = [
    "Your satisfaction is my priority, and I am here to assist you with any questions or concerns you may have.",
    "I am at your service, ready to provide you with the information and support you need.",
]

# Content writing logic
def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("content", "").strip()
    ContentByAI = ContentWriterAI(Topic)
    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(ContentByAI)
    OpenNotepad(file_path)
    return True

# YouTube Search
def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Open an app or web fallback
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[yellow]App open failed. Attempting web fallback...[/yellow]")

        def extract_Links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f'https://www.google.com/search?q={query}'
            headers = {'User-Agent': useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_Links(html)
            if links:
                webopen(links[0])
                return True
        return False

# Close an app
def CloseApp(app):
    if "chrome" in app:
        return True  # maybe handle differently?
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]Failed to close app:[/red] {e}")
        return False

# Volume and mute control
def System(command):
    def mute():
        keyboard.press_and_release("volume_mute")

    def unmute():
        keyboard.press_and_release("volume_mute")

    def volume_up():
        keyboard.press_and_release("volume_up")

    def volume_down():
        keyboard.press_and_release("volume_down")

    command = command.strip().lower()
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True

# Translate commands and execute
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        command = command.strip().lower()

        if command.startswith("open "):
            if "open it" in command or "open file" in command:
                continue
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(search, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        elif command.startswith("general ") or command.startswith("realtime "):
            # Reserved for chatbot or realtime search
            continue

        else:
            print(f"[red]No Function Found for:[/red] {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        yield result

# Execute automation
async def Automination(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True
