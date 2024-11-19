from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests

application = Flask(__name__)
CORS(application)

# Store generated images in memory
generated_images = []
is_Generating  = False

def generate_image(prompt):
    CLOUDFLARE_ACCOUNT_ID = '1c07109196bbec30982c032f3ad977c8'
    CLOUDFLARE_API_TOKEN = 'L0eS5FEsoxBIa4P6UFz_4zISLnMD9xo_MEGVHQ4-'

    api_url = f'https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0'
    payload = {'prompt': prompt}
    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        print(f'Error: {response.status_code} - {response.text}')
        return None

def add_text_to_image(image_data, text):
    image = Image.open(BytesIO(image_data))
    draw = ImageDraw.Draw(image)
    font_size = 30  # Increased font size
    font = ImageFont.truetype("arial.ttf", font_size)  # Using Arial font
    text_position = (10, 10)
    text_color = (255, 255, 0)  # Yellow color
    draw.text(text_position, text, fill=text_color, font=font)
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

def generate_scenes(prompt):
    api_key = "AIzaSyCaNNoRlBGXBLbzkD6pT-DXZp9fjBF04qM"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Break down the following story into scenes break each scene with ; or 'Scene': {prompt}")

    if not response or not response.text:
        return []
    
    scenes = [scene.strip() for scene in response.text.split('Scene') or response.text.split('Page') if scene.strip()]
    return scenes

@application.route('/generate-images', methods=['POST'])
def generate_images_endpoint():
    global is_Generating
    data = request.json
    prompt = data.get('prompt')
    is_Generating = True

    if not prompt or not isinstance(prompt, str):
        return jsonify({'error': 'A valid prompt is required'}), 400

    scenes = generate_scenes(prompt)
    images = []
    for scene in scenes:
        if scene:
            print(f"Generating image for scene: {scene}")
            image_data = generate_image("in manga style with subtitle " + scene)
            if image_data:
                image_with_text = add_text_to_image(image_data, scene)
                images.append(image_with_text)
                generated_images.append(image_with_text)  # Store the generated image
            else:
                return jsonify({'error': 'Failed to generate one or more images'}), 500

    images_base64 = [base64.b64encode(image).decode('utf-8') for image in images]
    is_Generating = False
    generated_images.clear()
    return jsonify({'images': images_base64})

@application.route('/images', methods=['GET'])
def get_images():
    global is_Generating
    if is_Generating:

        """Return all generated images in base64 format."""
        images_base64 = [base64.b64encode(image).decode('utf-8') for image in generated_images]
        return jsonify({'images': images_base64})
    else:
        return jsonify({'message': 'No images are being generated at the moment.'})

if __name__ == '__main__':
    application.run(debug=True)