import requests


def get_geocode_info(zip_code):
    base_url = 'https://geocode.maps.co/search'
    params = {'q': '%s+US' % zip_code}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)
        return data
    except requests.RequestException as e:
        print(f"Error making request: {e}")
        return None

def get_lat_long(zip_code):
    data = get_geocode_info(zip_code)
    if len(data) < 1:
        return None

    result = data[0]
    return result['lat'], result['lon']

