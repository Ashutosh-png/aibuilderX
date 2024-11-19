from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from flask_cors import CORS
import os
import zipfile
from io import BytesIO

app = Flask(__name__)
CORS(app)

def generate_code(prompt):
    """Generates code based on the provided prompt."""
    api_key = "AIzaSyB1HnatKme48GvmTf_e28hwzCGyM4LT0cY"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    clean_code = "\n".join(line for line in response.text.split("\n") if not line.strip().startswith("```"))
    return clean_code

@app.route('/generate_code', methods=['POST'])
def generate_api_code():
    """API endpoint to generate code."""
    data = request.get_json()
    prompt = data.get('prompt')
    backend_language = data.get('backend_language')
    
    backend_prompt = f"Create a {backend_language} backend for: {prompt}"
    frontend_prompt = f"Create a React frontend for: {prompt}"
    
    backend_code = generate_code(backend_prompt)
    frontend_code = generate_code(frontend_prompt)

    # Adjust file extension based on the language
    file_extension = {
        "python": "py",
        "node.js": "js",
        "ruby": "rb",
        "java": "java",
        "php": "php",
        "go": "go"
        # Add more languages as needed
    }.get(backend_language.lower(), "txt")  # Default to txt if language is not recognized

    # Write backend code to file
    backend_file_name = f"backend.{file_extension}"
    with open(backend_file_name, 'w') as file:
        file.write(backend_code)

    # Write frontend code to file
    frontend_file_name = "App.js"
    with open(frontend_file_name, 'w') as file:
        file.write(frontend_code)

    # Create zip file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(backend_file_name)
        zip_file.write(frontend_file_name)

    zip_buffer.seek(0)

    return send_file(zip_buffer, as_attachment=True, download_name='generated_code.zip', mimetype='application/zip')

if __name__ == "__main__":
    app.run(debug=True)

