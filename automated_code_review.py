import os
import openai
from datetime import datetime

# Set your OpenAI API Key
openai.api_key = "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"

# File paths for analysis
files_to_analyze = [
    "app.py",
    "ai_integration.py",
    "plaid_integration.py",
    "models.py",
]

# Directory for saving modified files
output_directory = "modified_files"

# Function to read file content
def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Function to analyze and modify files
def analyze_and_modify_file(file_path):
    content = read_file(file_path)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly skilled software developer."},
                {"role": "user", "content": f"Analyze the following Python file and suggest improvements. Then apply the changes and provide a modified version:\n\n{content}"}
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        modified_content = response.choices[0].message["content"]
        return modified_content
    except Exception as e:
        return f"Error analyzing file {file_path}: {str(e)}"

# Main function to process files
def process_files(files):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    summary = []
    for file_path in files:
        print(f"Processing {file_path}...")
        modified_content = analyze_and_modify_file(file_path)
        output_file = os.path.join(output_directory, os.path.basename(file_path))
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(modified_content)
        summary.append(f"File: {file_path} -> Modified and saved as {output_file}")
    
    # Save summary
    summary_file = os.path.join(output_directory, "summary.txt")
    with open(summary_file, "w", encoding="utf-8") as file:
        file.write("\n".join(summary))
    
    print("Processing complete. Summary saved.")
    return summary

# Schedule the task
if __name__ == "__main__":
    summary = process_files(files_to_analyze)
    print("\n".join(summary))
