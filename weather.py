# Scrapes data from AmbientWeather to Postgres
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import psycopg2
from psycopg2 import sql
from decimal import Decimal


# Establish a connection to the database
conn = psycopg2.connect(**{
    "dbname": "monitoring",
    "user": "adam",
    "password": "adam",
    "host": "localhost",
})
cur = conn.cursor()


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
                item_value = value_element[
                    "value"
                ].strip()  # Extract the value attribute
                data[field_name] = item_value
                continue
time_format = "%H:%M %m/%d/%Y"
naive_dt = datetime.strptime(data.pop("time"), time_format)
eastern = pytz.timezone("US/Eastern")
aware_dt = eastern.localize(naive_dt)
data["time"] = aware_dt
column_names = data.keys()
column_values = data.values()
weather_insert = sql.SQL("INSERT INTO weather ({}) VALUES ({})").format(
    sql.SQL(",").join(map(sql.Identifier, column_names)),
    sql.SQL(",").join(sql.Placeholder() * len(column_values))
)

try:
    cur.execute(weather_insert, list(column_values))
    conn.commit()
except psycopg2.Error as e:
    conn.rollback()
finally:
    # Close the cursor and the connection
    cur.close()
    conn.close()
