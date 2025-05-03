# Ticketmaster API to pull concerts based off: city, genre, or artist
# Save results as a JSON or CSV file in cache
# API Key: kT4Hd2l1jHPGK9rqEY6OH16P0EJCK8qt

from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

def get_concert_data(city="Syracuse", size=20):
    api_key = "kT4Hd2l1jHPGK9rqEY6OH16P0EJCK8qt"
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": api_key,
        "city": city,
        "classificationName": "music",
        "size": size
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code}")
    data = response.json()

    # Save to cache
    os.makedirs("code/cache", exist_ok=True)
    with open("code/cache/concert_data.json", "w") as f:
        json.dump(data, f, indent=2)
    return data
