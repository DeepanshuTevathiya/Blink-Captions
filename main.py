from flask import Flask, render_template, request
import base64
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

load_dotenv()
api_key = os.getenv("OpenAi_API")
client = OpenAI(api_key=api_key)


def encode_image(img):
        return base64.b64encode(img.read()).decode("utf-8")

prompt = """
Generate caption of provided image in 4 distinct tone as described:

Catption Type 1: Formal; Description: Professional, objective, 2-3 sentences; Example Output :"A golden retriever runs across a sandy 
coastal beach under clear skies."

Catption Type 2: Casual; Description: Conversational, warm, friendly tone; Example Output :"Look at this happy pup going full speed 
on the beach!"

Catption Type 3: SEO; Description: Keyword-rich, 15-25 words, search-optimised ; Example Output :"Golden retriever running on beach, 
happy dog outdoor exercise, pet photography summer coastal"

Catption Type 4: Alt-Text; Description: WCAG 2.1 compliant, under 125 characters; Example Output :"A golden retriever running on a sandy 
beach near ocean waves"

Important: The examples above correspond to a specific example image and are provided only to demonstrate the expected style and format. 
    Analyze the actual uploaded image and generate original captions based on its contents. Do not copy, reuse, or closely paraphrase the example captions.

Return only valid json.
{
    "formal": "caption here",
    "casual": "caption here",
    "seo": "caption here",
    "alt_text": "caption here"
}

Do not include markdown, explanations, code blocks, or any text outside the JSON object.
"""

@app.route("/", methods=["GET","POST"])
def home():
    img = request.files.get("image")

    if request.method == "GET" or img is None or img.filename == "":
        return render_template("index.html")
    
    if not img.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        return render_template("index.html", msg="Please upload a valid image file.")

    base64_image = encode_image(img)

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": "Generate captions based on the uploaded image and the user's instructions. Use any examples only as inspiration for style and structure, not as content to copy. Analyze the image and produce original captions."
            },
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    captions = json.loads(response.output_text)
    return render_template(
         "index.html",
         captions=captions
         )


if __name__ == "__main__":
    app.run(debug=True)