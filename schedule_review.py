import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from datetime import datetime
import os
import openai

# Email credentials
EMAIL_ADDRESS = "reid.reusch@gmail.com"  # Replace with your Gmail address
EMAIL_PASSWORD = "itgfcxghasliqdbl"   # Replace with your Gmail app password
RECIPIENT_EMAIL = "rreusch2@murraystate.edu"  # Replace with recipient's email


def send_email_notification(subject, body):
    """
    Sends an email notification using Gmail SMTP.
    """
    try:
        # Create email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject

        # Add email body
        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def read_multiple_files(file_paths):
    """
    Reads multiple files and combines their content for unified analysis.
    """
    combined_content = ""
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                combined_content += f"\n# File: {file_path}\n" + f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    return combined_content

def analyze_files(file_paths):
    """
    Analyzes multiple files together using OpenAI GPT.
    """
    combined_content = read_multiple_files(file_paths)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled software reviewer."},
                {
                    "role": "user",
                    "content": f"Analyze the following code from multiple files, suggesting improvements, "
                               f"refactoring, and detecting potential issues:\n\n{combined_content}"
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error during OpenAI analysis: {e}"

def save_analysis_results(suggestions):
    """
    Save analysis suggestions to a file.
    """
    output_file = "multi_file_analysis_suggestions.txt"
    with open(output_file, "w") as f:
        f.write(suggestions)
    print(f"Analysis complete. Suggestions saved to {output_file}.")
    return output_file

def scheduled_task():
    """
    Task to run analysis and notify via email.
    """
    print("Starting scheduled review...")
    file_paths = [
        "C:/Users/reidr/OneDrive/Desktop/APP/Financial-Planning-APP/app.py",
        "C:/Users/reidr/OneDrive/Desktop/APP/Financial-Planning-APP/ai_integration.py",
        "C:/Users/reidr/OneDrive/Desktop/APP/Financial-Planning-APP/plaid_integration.py",
        "C:/Users/reidr/OneDrive/Desktop/APP/Financial-Planning-APP/models.py"
    ]
    suggestions = analyze_files(file_paths)
    output_file = save_analysis_results(suggestions)

    # Prepare email body with detailed analysis results
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email_body = f"Scheduled analysis completed at {timestamp}.\n\nCode Review Analysis:\n\n{suggestions}\n\n"

    # Send email with analysis results
    send_email_notification("Scheduled Code Review Completed", email_body)

# Schedule the task
schedule.every().day.at("15:00").do(scheduled_task)  # Run daily at 3:45 AM
print("Scheduler started. Waiting for scheduled tasks...")

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
