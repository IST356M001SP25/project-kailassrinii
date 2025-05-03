from dotenv import load_dotenv
import os
from code.extract import get_concert_data

# Load env 
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
data = get_concert_data()
