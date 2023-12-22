import requests
from bs4 import BeautifulSoup
url = 'http://10.1.1.150/livedata.htm'

# Send an HTTP GET request to the URL
response = requests.get(url)

# Ensure the request was successful with response.status_code == 200

# Parse the HTML content of the page with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize an empty dictionary to store results
data = {}

# Find all 'tr' elements
for row in soup.find_all('tr'):
    # Find 'div' for the name and 'input' for the value within each 'tr'
    item_name_element = row.find('div', class_='item_1')
    value_element = row.find('input', class_='item_2')
    
    # If both elements are found, extract the text and value
    if item_name_element and value_element:
        item_name = item_name_element.text.strip()
        item_value = value_element['value'].strip()  # Extract the value attribute
        data[item_name] = item_value

# Output the data
for name, value in data.items():
    print(f"{name}: {value}")
