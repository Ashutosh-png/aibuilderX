import os
import shutil
import re
import google.generativeai as genai

def generate_code():
    api_key = input("Enter API key: ")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    prompt = input("Enter your prompt (e.g., 'Create a Spring Boot RESTful API for a Todo application with separate files for repository, service, controller, and main class, and include application.properties and pom.xml files'): ")
    response = model.generate_content(prompt)
    clean_code = "\n".join(line for line in response.text.split("\n") if not line.strip().startswith("```"))

    # Save the generated code to a temporary file
    temp_file = "temp_code.txt"
    with open(temp_file, "w", encoding="utf-8") as file:
        print(clean_code)
        file.write(clean_code)

    # Create a temporary directory
    temp_dir = "temp_project"
    os.makedirs(temp_dir, exist_ok=True)

    # Create the project structure manually
    os.makedirs(os.path.join(temp_dir, "src", "main", "java", "com", "example", "demo"))
    os.makedirs(os.path.join(temp_dir, "src", "main", "resources"))

    # Extract the repository, service, controller, and main class code from the generated code
    repository_code = re.search(r'// Repository([\s\S]*?)// Service', clean_code)
    service_code = re.search(r'// Service([\s\S]*?)// Controller', clean_code)
    controller_code = re.search(r'// Controller([\s\S]*?)// Main', clean_code)
    main_code = re.search(r'// Main([\s\S]*)', clean_code)

    # Extract the application.properties and pom.xml files from the generated code
    application_properties = re.search(r'# application.properties([\s\S]*?)# pom.xml', clean_code)
    pom_xml = re.search(r'# pom.xml([\s\S]*)', clean_code)

    # Write the extracted code to separate files
    with open(os.path.join(temp_dir, "src", "main", "java", "com", "example", "demo", "Repository.java"), "w", encoding="utf-8") as file:
        if repository_code:
            file.write(repository_code.group(1).strip())

    with open(os.path.join(temp_dir, "src", "main", "java", "com", "example", "demo", "Service.java"), "w", encoding="utf-8") as file:
        if service_code:
            file.write(service_code.group(1).strip())

    with open(os.path.join(temp_dir, "src", "main", "java", "com", "example", "demo", "Controller.java"), "w", encoding="utf-8") as file:
        if controller_code:
            file.write(controller_code.group(1).strip())

    with open(os.path.join(temp_dir, "src", "main", "java", "com", "example", "demo", "MainClass.java"), "w", encoding="utf-8") as file:
        if main_code:
            file.write(main_code.group(1).strip())

    with open(os.path.join(temp_dir, "src", "main", "resources", "application.properties"), "w", encoding="utf-8") as file:
        if application_properties:
            file.write(application_properties.group(1).strip())

    with open(os.path.join(temp_dir, "pom.xml"), "w", encoding="utf-8") as file:
        if pom_xml:
            file.write(pom_xml.group(1).strip())

    # Remove the temporary file
    os.remove(temp_file)

    # Compress the generated project
    project_zip = "generated_project.zip"
    shutil.make_archive("generated_project", "zip", temp_dir)

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

    print(f"Generated Spring Boot project '{project_zip}' successfully.")

if __name__ == "__main__":
    generate_code()