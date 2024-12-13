import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Create the model.
model = genai.GenerativeModel('gemini-pro')

# Prompt the model.
response = model.generate_content("What are 3 tips for saving money?")

# Print the response
print(response.text)