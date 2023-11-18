import requests
from bs4 import BeautifulSoup

responseData = requests.get('https://allevents.in/api/events/find-events-from-nearby-cities')
print(responseData.json()) 
