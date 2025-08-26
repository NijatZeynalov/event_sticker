# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import mimetypes
import os
import google.generativeai as genai
from google.generativeai import types


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")
    return file_name


def generate(background_image_data, character_image_data):
    # IMPORTANT: Your API key was leaked. Please go to your Google Cloud console
    # and revoke this key immediately.
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No GOOGLE_API_KEY set for Google API")

    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.0-flash-preview-image-generation"
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(inline_data=types.Blob(data=background_image_data, mime_type="image/png")),
                types.Part(inline_data=types.Blob(data=character_image_data, mime_type="image/png")),
                types.Part.from_text(text="""Use the first image as the background, and place the character from the second image in the middle of it. The final image should be in a classic Disney animation style with bold lines, fairy-tale aesthetics, and lively expressions."""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"generated_image_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            return data_buffer
        else:
            print(chunk.text)

if __name__ == "__main__":
    with open("background/stage.png", "rb") as f:
        background_data = f.read()
    with open("character/pikachu.png", "rb") as f:
        character_data = f.read()
    generate(background_data, character_data)
