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
    print("Generated response:", response)  # Debugging statement
    if not response or not response.text:
        return ""
    clean_code = "\n".join(line for line in response.text.split("\n") if not line.strip().startswith("```"))
    return clean_code

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

    print("Backend code:", backend_code)  # Debugging statement
    print("Frontend code:", frontend_code)  # Debugging statement

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

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in backend_files.items():
            zip_file.writestr(f"backend/{filename}", content)
        for filename, content in frontend_files.items():
            zip_file.writestr(f"frontend/{filename}", content)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='generated_code.zip', mimetype='application/zip')

if __name__ == "__main__":
    app.run(debug=True)