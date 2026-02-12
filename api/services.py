import requests

class ArtInstituteService:
    BASE_URL = "https://api.artic.edu/api/v1/artworks"

    @classmethod
    def get_place(cls, external_id):
        """
        Fetch place details from Art Institute API.
        Returns a dictionary with 'external_id' and 'name' if found, else None.
        """
        try:
            url = f"{cls.BASE_URL}/{external_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data')
                if data:
                    return {
                        'external_id': data.get('id'),
                        'name': data.get('title'),
                    }
            return None
        except requests.RequestException:
            # In a real app, log error
            return None
