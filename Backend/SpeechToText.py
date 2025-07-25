from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import mtranslate as mt  # Optional for translation

# Load env vars
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"

# Full working Speech Recognition HTML
HtmlCode = f"""<!DOCTYPE html>
<html lang="en">
<head><title>Speech Recognition</title></head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="stop" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output" style="font-size:24px;"></p>

    <script>
        var output = document.getElementById('output');
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = "{InputLanguage}";
        recognition.continuous = false;
        recognition.interimResults = false;

        function startRecognition() {{
            output.innerText = "";
            recognition.start();
        }}

        function stopRecognition() {{
            recognition.stop();
        }}

        recognition.onresult = function(event) {{
            var transcript = event.results[0][0].transcript;
            output.innerText = transcript;
        }};

        recognition.onerror = function(event) {{
            output.innerText = "Error: " + event.error;
        }};
    </script>
</body>
</html>
"""

# Save the HTML file
os.makedirs("Data", exist_ok=True)
with open(r"Data\Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Chrome options for Selenium
chrome_options = Options()
chrome_options.add_argument("--use-fake-device-for-media-stream")
# chrome_options.add_argument("--headless=new")  # Use only in production
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Setup driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Assistant status writer
def SetAssistantStatus(Status):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Query format cleaner
def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["what", "who", "where", "when", "why", "how"]
    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip('.?!') + "?"
    else:
        new_query = new_query.rstrip('.?!') + "."
    return new_query.capitalize()

# Translation function
def UniversalTranslator(Text):
    translated = mt.translate(Text, "en", "auto")
    return translated.capitalize()

# Main recognition function
def SpeechRecognition():
    driver.get("file://" + os.path.abspath("Data/Voice.html"))
    driver.find_element(By.ID, "start").click()
    time.sleep(0.5)

    while True:
        try:
            text = driver.find_element(By.ID, "output").text
            if text and not text.lower().startswith("error"):
                print(f"[DEBUG] Captured: {text}")
                driver.find_element(By.ID, "stop").click()
                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(text))
        except Exception:
            pass
        time.sleep(0.2)

# Test run
if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        print(f"You said: {result}")
