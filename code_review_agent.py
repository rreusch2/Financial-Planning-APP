import os
import openai
import argparse

# Set your OpenAI API key
openai.api_key = "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"

def read_specific_files(file_paths, max_lines=100):
    """
    Read the specified Python files, limiting the number of lines read.
    """
    python_files = {}
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                limited_content = "".join(lines[:max_lines])  # Limit to the first `max_lines`
            python_files[file_path] = limited_content
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
    return python_files

def summarize_code_with_gpt(file_path, code_content):
    """
    Use GPT-4 to summarize the code for inclusion in the unified analysis.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a highly skilled software assistant."},
                {
                    "role": "user",
                    "content": f"Summarize the following Python code from {file_path} for a code review. "
                               f"Highlight its purpose, key functions, and structure:\n\n{code_content}"
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error summarizing code: {str(e)}"

def summarize_files(file_contents):
    """
    Summarize all files and combine the summaries.
    """
    summaries = {}
    for file_path, code_content in file_contents.items():
        print(f"Summarizing {file_path}...")
        summaries[file_path] = summarize_code_with_gpt(file_path, code_content)
    return summaries

def analyze_files_together_with_gpt(summaries):
    """
    Combine file summaries and analyze them together with GPT-4.
    """
    combined_summary = "\n\n".join(
        [f"Summary for {file_path}:\n{summary}" for file_path, summary in summaries.items()]
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a highly skilled code review assistant."},
                {
                    "role": "user",
                    "content": f"Based on the following summaries of Python files, analyze how they work together. "
                               f"Provide recommendations for improvements, refactoring, and performance optimization:\n\n{combined_summary}"
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error analyzing combined files: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Code Review Agent for specific files.")
    parser.add_argument("file_paths", nargs="+", help="Paths to the Python files to analyze.")
    parser.add_argument("--max_lines", type=int, default=100, help="Maximum lines to read from each file.")
    args = parser.parse_args()

    # Read and summarize specified files
    file_contents = read_specific_files(args.file_paths, max_lines=args.max_lines)
    summaries = summarize_files(file_contents)

    # Unified analysis of all file summaries
    unified_analysis = analyze_files_together_with_gpt(summaries)
    print("\n=== Unified Analysis ===\n")
    print(unified_analysis)
