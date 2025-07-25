import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load env
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-Wavenet-A")

# Async text-to-speech file generator
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)

    communite = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communite.save(file_path)

# Sync playback
def TTS(Text, func=lambda r=None: True):
    for attempt in range(3):
        try:
            asyncio.run(TextToAudioFile(Text))
            pygame.mixer.init()
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if func() is False:
                    break
                pygame.time.Clock().tick(10)

            return True
        except pygame.error as e:
            print(f"[TTS ERROR] {e}")
        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"[CLEANUP ERROR] {e}")

# High-level TTS with intelligent response shortening
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
    ]

    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Data[:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)

# Test
if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the Text: "))
