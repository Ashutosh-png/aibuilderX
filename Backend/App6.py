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
    api_key = "AIzaSyB1HnatKme48GvmTf_e28hwzCGyM4LT0cY"  # Replace with your actual API key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    if not response or not response.text:
        return ""
    clean_code = "\n".join(line for line in response.text.split("\n") if not line.strip().startswith("```"))
    return clean_code

def get_file_names(prompt, backend_language, type):
    code = generate_code(f"{prompt} only give {type} end file names required to make this if frontend is react and backend is {backend_language}")
    file_names = [line.strip() for line in code.split('\n') if line.strip()]
    return file_names

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
    if not files and current_content:
        files[f"{prefix}_default.{extension}"] = "\n".join(current_content)
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
    backend_file_names = get_file_names(prompt, backend_language, 'back')
    backend_files = {filename: backend_code for filename in backend_file_names}
    frontend_files = split_code_into_files(frontend_code, "frontend", "js")
    return backend_files, frontend_files

def create_code_files(backend_files, frontend_files, backend_file_names):
    """Creates code files from the generated code."""
    code_files = {}
    backend_folder = "backend"
    if not os.path.exists(backend_folder):
        os.makedirs(backend_folder)
    for filename in backend_file_names:
        if filename in backend_files:
            code_files[f"{backend_folder}/{filename}"] = backend_files[filename]
        else:
            code_files[f"{backend_folder}/{filename}"] = ""
    frontend_folder = "frontend"
    if not os.path.exists(frontend_folder):
        os.makedirs(frontend_folder)
    for filename, content in frontend_files.items():
        code_files[f"{frontend_folder}/{filename}"] = content
    return code_files

def zip_code_files(code_files):
    """Zips the code files into a single zip file."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in code_files.items():
            zip_file.writestr(filename, content)
            if os.path.dirname(filename):
                zip_file.writestr(os.path.dirname(filename) + "/", "")
    zip_buffer.seek(0)
    return zip_buffer

@app.route('/generate_code', methods=['POST'])
def generate_api_code():
    """API endpoint to generate code."""
    data = request.get_json()
    prompt = data.get('prompt')
    backend_language = data.get('backend_language')
    backend_file_names = get_file_names(prompt, backend_language, 'back')
    backend_files, frontend_files = generate_code_files(prompt, backend_language)
    code_files = create_code_files(backend_files, frontend_files, backend_file_names)
    zip_buffer = zip_code_files(code_files)
    return send_file(zip_buffer, as_attachment=True, download_name='generated_code.zip', mimetype='application/zip')

if __name__ == "__main__":
    app.run(debug=True)