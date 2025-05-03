from dotenv import load_dotenv
import os
from code.extract import get_concert_data

# Explicitly load the .env file from the root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Run the concert data fetch
data = get_concert_data()
