import requests
from config import API_KEY
import json


def fetch_data(title):
    key = "af27ecd8"
    url = f"https://www.omdbapi.com/?apikey={key}&t={title}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # raise an exception for a bad status code
        data = response.json()
        return data
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error: {e}")