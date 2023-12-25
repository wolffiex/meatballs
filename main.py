import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from decimal import Decimal
url = "http://10.1.1.150/livedata.htm"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Ensure the request was successful with response.status_code == 200

# Parse the HTML content of the page with BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Initialize an empty dictionary to store results
data = {}

SCRAPED_FIELDS = {
    "Receiver Time": "time",
    "Indoor Temperature": "indoor_temp",
    "Relative Pressure": "pressure",
    "Outdoor Temperature": "outdoor_temp",
    "Humidity": "humidity",
    "Wind Speed": "wind_speed",
    "Solar Radiation": "solar_radiation",
    "UVI": "uvi",
    "Hourly Rain Rate": "rain_rate",
}

# Find all 'tr' elements
for row in soup.find_all("tr"):
    # Find 'div' for the name and 'input' for the value within each 'tr'
    item_name_element = row.find("div", class_="item_1")
    value_element = row.find("input", class_="item_2")

    # If both elements are found, extract the text and value
    if item_name_element and value_element:
        item_name = item_name_element.text.strip()
        for sub_str, field_name in SCRAPED_FIELDS.items():
            if sub_str in item_name:
                item_value = value_element["value"].strip()  # Extract the value attribute
                data[field_name] = item_value
                continue
time_format = "%H:%M %m/%d/%Y"
naive_dt = datetime.strptime(data.pop('time'), time_format)
eastern = pytz.timezone('US/Eastern')
aware_dt = eastern.localize(naive_dt)
print(f"time: {aware_dt}")
# Output the data
for name, value in data.items():
    print(f"{name}: {Decimal(value)}")
