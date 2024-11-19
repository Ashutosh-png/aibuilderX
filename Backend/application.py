from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from flask_cors import CORS
import os
import zipfile
from io import BytesIO
import base64
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

# def add_text_to_image(image_data, text):
#     image = Image.open(BytesIO(image_data))
#     draw = ImageDraw.Draw(image)
#     font_size = 30  # Increased font size
#     font = ImageFont.truetype("arial.ttf", font_size)  # Using Arial font
#     text_position = (10, 10)
#     text_color = (255, 255, 0)  # Yellow color
#     draw.text(text_position, text, fill=text_color, font=font)
#     img_byte_arr = BytesIO()
#     image.save(img_byte_arr, format='JPEG')
#     img_byte_arr.seek(0)
#     return img_byte_arr.getvalue()

def add_text_to_image(image_data, text):
    image = Image.open(BytesIO(image_data))
    draw = ImageDraw.Draw(image)
    font_size = 30  # Increased font size
    #font = ImageFont.truetype("arial.ttf", font_size)  # Using Arial font
    font = ImageFont.load_default()
    text_color = (255, 255, 0)  # Yellow color

    # Define the maximum width for the text
    max_width = image.width - 20  # Leave some padding

    # Split the text into lines that fit within the max width
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        # Check if adding the next word would exceed the max width
        test_line = f"{current_line} {word}".strip()
        # Use textbbox to get the bounding box of the text
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]  # Calculate width from bbox

        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word  # Start a new line with the current word

    # Add the last line if it exists
    if current_line:
        lines.append(current_line)

    # Draw each line of text on the image
    y_text = 10  # Starting position for the text
    for line in lines:
        draw.text((10, y_text), line, fill=text_color, font=font)
        y_text += font_size + 5  # Move down for the next line

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

def generate_scenes(prompt):
    api_key = "AIzaSyCaNNoRlBGXBLbzkD6pT-DXZp9fjBF04qM"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    #response = model.generate_content(f"Break down the following story into scenes break each scene with ; or 'Scene': {prompt}")
    response = model.generate_content(f"Break down the following story into story telling scenes break each scene with ; or 'Scene': {prompt}")

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




def generate_code(prompt):
    """Generates code based on the provided prompt."""
    #api_key = "AIzaSyB1HnatKme48GvmTf_e28hwzCGyM4LT0cY"  # Replace with your actual API key
    api_key="AIzaSyCaNNoRlBGXBLbzkD6pT-DXZp9fjBF04qM"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
   # print("Generated response:", response)  # Debugging statement
    if not response or not response.text:
        return ""
    clean_code = "\n".join(line for line in response.text.split("\n") if not line.strip().startswith("```"))
    return clean_code


def front_end_file_names(prompt,backend_language):
    code = generate_code(prompt+" only give front end file name required to make this if frontend is react and backend is "+backend_language)
    print(code)


def back_end_file_names(prompt,backend_language):
    code = generate_code(prompt+" only give back end file name required to make this if frontend is react and backend is "+backend_language)
    print(code)






def split_code_into_files(code, prefix, extension):
    """Splits code into multiple files based on some logic, e.g., comments or sections."""
    files = {}
    current_file = None
    current_content = []

    for line in code.split('\n'):
        if line.strip().startswith("// File:"):  # Assuming files are denoted by comments
            if current_file and current_content:
                files[current_file] = "\n".join(current_content)
            current_file = line.strip()[8:].strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_file and current_content:
        files[current_file] = "\n".join(current_content)

    # If no files are found, create a default file
    if not files and current_content:
        files[f"{prefix}_default.{extension}"] = "\n".join(current_content)

    print("Split files:", files)  # Debugging statement
    return files

def generate_code_files(prompt, backend_language):
    """Generates code files based on the provided prompt."""
    backend_prompt = f"Create a {backend_language} backend for: {prompt}"
    frontend_prompt = f"Create a React frontend for: {prompt}"
    
    backend_code = generate_code(backend_prompt)
    frontend_code = generate_code(frontend_prompt)

    file_extension = {
        "python": "py",
        "node.js": "js",
        "ruby": "rb",
        "java": "java",
        "php": "php",
        "go": "go"
    }.get(backend_language.lower(), "txt")  # Default to txt if language is not recognized

    backend_files = split_code_into_files(backend_code, "backend", file_extension)
    frontend_files = split_code_into_files(frontend_code, "frontend", "js")

    return backend_files, frontend_files

def create_code_files(backend_files, frontend_files):
    """Creates code files from the generated code."""
    code_files = {}
    for filename, content in backend_files.items():
        code_files[f"backend/{filename}"] = content
    for filename, content in frontend_files.items():
        code_files[f"frontend/{filename}"] = content
    return code_files

def zip_code_files(code_files):
    """Zips the code files into a single zip file."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in code_files.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

@application.route('/generate_code', methods=['POST'])
def generate_api_code():
    """API endpoint to generate code."""
    data = request.get_json()
    prompt = data.get('prompt')
    backend_language = data.get('backend_language')
    

    front_end_file_names(prompt,backend_language)
    print("       ")
    back_end_file_names(prompt,backend_language)

    print("after the file names code ")
    backend_files, frontend_files = generate_code_files(prompt, backend_language)
    code_files = create_code_files(backend_files, frontend_files)
    zip_buffer = zip_code_files(code_files)

    return send_file(zip_buffer, as_attachment=True, download_name='generated_code.zip', mimetype='application/zip')

if __name__ == "__main__":
    application.run(debug=True)