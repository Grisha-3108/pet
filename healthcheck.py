import httpx

from config import settings



if __name__ == '__main__':
    try:
        response = httpx.get(f'http://localhost:{settings.port}/ping')
        response.raise_for_status()
        result = response.json()
        assert result['message'] == 'ok'
    except Exception as e:
        exit(1)