import os
import requests
import pendulum
import json
from dotenv import load_dotenv
import sys
from pathlib import Path

# load env files
load_dotenv()

# part of current dir
app_path = Path(__file__).parent

# Environment variable for API key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_DOMAIN = "http://dataservice.accuweather.com"

# emojis that accuweather uses
emojis = {
    1: "☀️",
    2: "☀️",
    3: "🌤",
    4: "🌤",
    5: "🌤",
    6: "🌥",
    7: "☁️",
    8: "☁️",
    11: "🌫",
    12: "🌧",
    13: "🌦",
    14: "🌦",
    15: "⛈",
    16: "⛈",
    17: "🌦",
    18: "🌧",
    19: "🌨",
    20: "🌨",
    21: "🌨",
    22: "❄️",
    23: "❄️",
    24: "🌧",
    25: "🌧",
    26: "🌧",
    29: "🌧",
    30: "🥵",
    31: "🥶",
    32: "💨",
}

dayBubbleWidths = {
    "Monday": 235,
    "Tuesday": 235,
    "Wednesday": 260,
    "Thursday": 245,
    "Friday": 220,
    "Saturday": 245,
    "Sunday": 230,
}

# Time since graduating
today = pendulum.now()
todayDay = today.format("dddd")

psTime = pendulum.instance(today).diff_for_humans(
    pendulum.datetime(2023, 12, 14), absolute=True
)

# Today's weather
locationKey = "331416"  # Bellingham
url = f"forecasts/v1/daily/1day/{locationKey}?apikey={WEATHER_API_KEY}"

try:
    response = requests.get(f"{WEATHER_DOMAIN}/{url}")
    response.raise_for_status()
    json_data = response.json()

    degF = round(json_data["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"])
    degC = round((degF - 32) * 5 / 9)
    icon = json_data["DailyForecasts"][0]["Day"]["Icon"]

    with open(app_path / "template.svg", "r", encoding="utf-8") as file:
        data = file.read()

    data = data.replace("{degF}", str(degF))
    data = data.replace("{degC}", str(degC))
    data = data.replace("{weatherEmoji}", emojis[icon])
    data = data.replace("{psTime}", psTime)
    data = data.replace("{todayDay}", todayDay)
    data = data.replace("{dayBubbleWidth}", str(dayBubbleWidths[todayDay]))

    with open(app_path / "chat.svg", "w", encoding="utf-8") as file:
        file.write(data)

except requests.exceptions.RequestException as err:
    print(err, file=sys.stderr)
