import os
from dotenv import load_dotenv

# This line is crucial - it loads the .env file
load_dotenv()

# These lines read the keys from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")