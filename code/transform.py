# Clean the JSON and pull info: event name, date, venue, price, genre, venue  

import pandas as pd
import json

def load_and_transform():
    with open("code/cache/concert_data.json", "r") as f:
        raw = json.load(f)

    events = raw["_embedded"]["events"]
    rows = []
    for event in events:
        name = event["name"]
        date = event["dates"]["start"]["localDate"]
        time = event["dates"]["start"].get("localTime", "")
        venue = event["_embedded"]["venues"][0]

        city = venue.get("city", {}).get("name", "")
        venue_name = venue.get("name", "")
        url = event.get("url", "")
        image = event["images"][0]["url"]

        latitude = venue.get("location", {}).get("latitude")
        longitude = venue.get("location", {}).get("longitude")

        rows.append({
            "Name": name,
            "Date": date,
            "Time": time,
            "City": city,
            "Venue": venue_name,
            "Ticket URL": url,
            "Image": image,
            "Latitude": float(latitude) if latitude else None,
            "Longitude": float(longitude) if longitude else None
        })

    return pd.DataFrame(rows)
