import requests
from django.conf import settings


def get_all_cities():
    

     url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"

     headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": "wft-geo-db.p.rapidapi.com"
        }



     try:
           response = requests.get(url, headers=headers)
           response.raise_for_status()
           data = response.json()
           return data['data']
     except requests.exceptions.RequestException as e:
            print(f"error fetching cities {e}")
            return []