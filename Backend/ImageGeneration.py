import asyncio
import os
from random import randint
from PIL import Image
import requests
from dotenv import get_key
from time import sleep

# Set up HuggingFace API
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HUGGINGFACE_API_KEY')}"}

# Open generated images
def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")

    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)  # ✅ Fixed path join
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open image: {image_path}")

# Send prompt to HuggingFace API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# Generate 4 images concurrently
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    os.makedirs("Data", exist_ok=True)

    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{prompt.replace(' ', '_')}{i + 1}.jpg", 'wb') as f:
            f.write(image_bytes)

# Wrapper function to call generation + opening
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop to watch the file trigger
def watch_trigger_file():
    file_path = r"Frontend\Files\ImageGeneration.data"
    while True:
        try:
            with open(file_path, "r") as f:
                data: str = f.read()
            prompt, status = data.split(",")

            if status.strip() == "True":
                print("Generating Image ...")
                GenerateImages(prompt=prompt.strip())

                with open(file_path, "w") as f:
                    f.write("False,False")
                break
            else:
                sleep(1)
        except:
            sleep(1)

# Start watching the trigger
if __name__ == "__main__":
    watch_trigger_file()
