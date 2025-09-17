# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import mimetypes
import os


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")
    return file_name


def generate(background_image_data, character_image_data, subject, style):
    # Import SDK in-function and support both packages: google-genai and google-generativeai
    try:
        from google import genai  # google-genai
        from google.genai import types
    except Exception:
        import google.generativeai as genai  # google-generativeai
        from google.generativeai import types

    # IMPORTANT: Your API key was leaked. Please go to your Google Cloud console
    # and revoke this key immediately.
    api_key = 'YOUR_API_KEY'

    if not api_key:
        raise ValueError("No GOOGLE_API_KEY set for Google API")

    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.0-flash-preview-image-generation"

    style_prompts = {
        "ghibli": "the Ghibli style, painterly anime look, soft watercolor textures, lush natural environments, emotionally expressive characters with large eyes, subtle magical realism, nostalgic atmosphere, warm lighting, gentle brushwork.",
        "Muppet Realistic Style": "Muppet realistic style, 3D photo-realistic puppet look, visible stitching and felt fuzz, soft fabric textures, googly eyes, yarn hair, handmade materials under cinematic lighting, playful and exaggerated puppet expressions.",
        "Pixar 3D": "charming 3D animated style, clean, stylized character designs with expressive yet subtle facial animation, cinematic warm lighting, beautifully composed shots, high-quality polished textures, and a heartwarming tone. Emphasize storytelling through posture, expression, and framing.",
        "disney classic": "mid-century fairytale animation style, 2D cel animation with big expressive eyes, soft hand-painted backgrounds, gentle color gradients, magical lighting, graceful character poses, and a nostalgic storybook tone inspired by the golden age of animated films.",
        "Lego Style": "the Lego style, made entirely of plastic bricks, blocky shapes, visible stud textures, modular construction, bright primary colors, characters with iconic Lego faces and claw hands, 3D toy-like rendering."
    }

    # The style selected by the user is used as a key to get the corresponding prompt.
    # This directly uses the 'style' variable passed from the user's selection.
    style_prompt = style_prompts[style]
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(inline_data=types.Blob(data=background_image_data, mime_type="image/png")),
                types.Part(inline_data=types.Blob(data=character_image_data, mime_type="image/png")),
                types.Part.from_text(text=f"""Use the first image as the background, and place the character from the second image in the middle of it. The final image should be in {style_prompt}, with a {subject} theme."""),
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
    generate(background_data, character_data, "Sci-Fi", "ghibli")
