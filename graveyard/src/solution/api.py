import requests

def send(s:str, timeout:int=10):
  headers = {
    "Content-type": "text/plain",
    "Accept": "*/*",
  }
  url="https://icfpc2020-api.testkontur.ru/aliens/send?apiKey=0efd47509729415d884f297166f5e823"
  try:
    response = requests.post(url,
      data=s,
      headers=headers,
      timeout=timeout)
    return response
  except requests.exceptions.ConnectTimeout:
    raise TimeoutException(f"ConnectTimeout while accessing {url}")
  except requests.exceptions.ReadTimeout:
    raise TimeoutException(f"ReadTimeout while accessing {url}")
