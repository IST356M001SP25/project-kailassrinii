from code.extract import get_concert_data

if __name__ == "__main__":
    data = get_concert_data()
    print(f"Found {len(data.get('_embedded', {}).get('events', []))} events.")
