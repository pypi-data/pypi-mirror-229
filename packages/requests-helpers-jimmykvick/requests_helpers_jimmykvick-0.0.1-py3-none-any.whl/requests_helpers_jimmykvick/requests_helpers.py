import requests

def post_request(url, payload):
  try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
      print('Request POST exitoso')
      return response
    else:
      print(f"Error en el request POST: {response.status_code}")
      return response
  except Exception as e:
    print(f"Error en post_request: {e}")
    return False