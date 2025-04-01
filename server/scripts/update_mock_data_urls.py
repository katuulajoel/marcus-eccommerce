import os
import re

# Get the backend base URL from environment variables, with a default fallback
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# Dynamically determine the base directory and mock data file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_DATA_FILE = os.path.join(BASE_DIR, "db", "mock_data.sql")

def update_image_urls():
    # Read the mock data file
    with open(MOCK_DATA_FILE, "r") as file:
        content = file.read()

    # Regex pattern to find image_url fields
    pattern = r"(/media/[a-zA-Z0-9_/.-]+)"

    # Replace relative paths with full URLs
    updated_content = re.sub(pattern, f"{BACKEND_BASE_URL}\\1", content)

    # Write the updated content back to the file
    with open(MOCK_DATA_FILE, "w") as file:
        file.write(updated_content)

    print(f"Updated image URLs in {MOCK_DATA_FILE} with base URL: {BACKEND_BASE_URL}")

if __name__ == "__main__":
    update_image_urls()
