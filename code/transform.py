# Clean the JSON and pull key info: event name, date, venue, price, genre, location (have coordinates)

import json
import pandas as pd

# Load data
def load_and_transform(filepath="code/cache/concert_data.json"):
    with open(filepath, "r") as f:
        data = json.load(f)

    events = data.get("_embedded", {}).get("events", [])
    
    transformed = []
    for event in events:
        name = event.get("name")
        date = event.get("dates", {}).get("start", {}).get("localDate")
        time = event.get("dates", {}).get("start", {}).get("localTime")
        venue = event.get("_embedded", {}).get("venues", [{}])[0].get("name")
        city = event.get("_embedded", {}).get("venues", [{}])[0].get("city", {}).get("name")
        image_url = event.get("images", [{}])[0].get("url")
        ticket_url = event.get("url")

        transformed.append({
            "Name": name,
            "Date": date,
            "Time": time,
            "Venue": venue,
            "City": city,
            "Image": image_url,
            "Ticket URL": ticket_url
        })

    return pd.DataFrame(transformed)

