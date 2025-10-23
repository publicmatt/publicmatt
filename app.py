import sys
from pathlib import Path
from typing import ClassVar

import pendulum
import requests
from pydantic import Field
from pydantic_settings import BaseSettings, CliApp


class App(BaseSettings):
    """Application settings for weather SVG generator."""
    
    latitude: float = Field(
        default=48.7519,
        description="Latitude for weather location (default: Bellingham, WA)"
    )
    longitude: float = Field(
        default=-122.4787,
        description="Longitude for weather location (default: Bellingham, WA)"
    )
    grad_date: str = Field(
        default="2023-12-14",
        description="Graduation date in YYYY-MM-DD format"
    )
    template_path: Path = Field(
        default=Path("template.svg"),
        description="Path to template SVG file"
    )
    output_path: Path = Field(
        default=Path("chat.svg"),
        description="Path to output SVG file"
    )


    # Weather icon to emoji mapping (based on weather.gov icon URLs)
    WEATHER_EMOJIS: ClassVar = {
        "skc": "☀️",  # Sky Clear
        "few": "🌤",  # Few Clouds
        "sct": "⛅",  # Scattered Clouds
        "bkn": "🌥",  # Broken Clouds
        "ovc": "☁️",  # Overcast
        "wind_skc": "💨",  # Windy and Clear
        "wind_few": "💨",  # Windy and Few Clouds
        "wind_sct": "💨",  # Windy and Scattered Clouds
        "wind_bkn": "💨",  # Windy and Broken Clouds
        "wind_ovc": "💨",  # Windy and Overcast
        "snow": "❄️",  # Snow
        "rain_snow": "🌨",  # Rain/Snow
        "rain_sleet": "🌨",  # Rain/Sleet
        "snow_sleet": "🌨",  # Snow/Sleet
        "fzra": "🌧",  # Freezing Rain
        "rain_fzra": "🌧",  # Rain/Freezing Rain
        "snow_fzra": "🌨",  # Snow/Freezing Rain
        "sleet": "🌨",  # Sleet
        "rain": "🌧",  # Rain
        "rain_showers": "🌦",  # Rain Showers
        "rain_showers_hi": "🌦",  # Rain Showers (High)
        "tsra": "⛈",  # Thunderstorm
        "tsra_sct": "⛈",  # Scattered Thunderstorms
        "tsra_hi": "⛈",  # Thunderstorm (High)
        "tornado": "🌪",  # Tornado
        "hurricane": "🌀",  # Hurricane
        "tropical_storm": "🌀",  # Tropical Storm
        "dust": "🌫",  # Dust
        "smoke": "🌫",  # Smoke
        "haze": "🌫",  # Haze
        "hot": "🥵",  # Hot
        "cold": "🥶",  # Cold
        "blizzard": "🌨",  # Blizzard
        "fog": "🌫",  # Fog
    }

    DAY_BUBBLE_WIDTHS: ClassVar = {
        "Monday": 235,
        "Tuesday": 235,
        "Wednesday": 260,
        "Thursday": 245,
        "Friday": 220,
        "Saturday": 245,
        "Sunday": 230,
    }


    @staticmethod
    def get_weather_icon_code(icon_url: str) -> str:
        """Extract weather condition code from weather.gov icon URL.
        
        Example: https://api.weather.gov/icons/land/day/tsra,40?size=medium
        Returns: tsra
        """
        if not icon_url:
            return "skc"
        
        # Extract the condition from the URL path
        parts = icon_url.split("/")
        if len(parts) >= 2:
            # Get the last part and remove query parameters and comma-separated values
            condition = parts[-1].split("?")[0].split(",")[0]
            return condition
        return "skc"


    @classmethod
    def get_weather_emoji(cls, icon_url: str) -> str:
        """Get emoji for weather condition from icon URL."""
        code = cls.get_weather_icon_code(icon_url)
        return cls.WEATHER_EMOJIS.get(code, "☀️")


    @staticmethod
    def fetch_weather(lat: float, lon: float) -> tuple[int, int, str]:
        """Fetch weather data from weather.gov API.
        
        Returns:
            tuple: (temperature_f, temperature_c, icon_url)
        """
        # Weather.gov requires a User-Agent header
        headers = {
            "User-Agent": "(Weather SVG Generator, contact@example.com)"
        }
        
        # First, get the grid endpoint for this location
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        response = requests.get(points_url, headers=headers)
        response.raise_for_status()
        points_data = response.json()
        
        # Get the forecast URL
        forecast_url = points_data["properties"]["forecast"]
        
        # Fetch the forecast
        forecast_response = requests.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Get today's forecast (first period)
        today_forecast = forecast_data["properties"]["periods"][0]
        
        temp_f = today_forecast["temperature"]
        temp_c = round((temp_f - 32) * 5 / 9)
        icon_url = today_forecast["icon"]
        
        return temp_f, temp_c, icon_url


    def cli_cmd(self) -> None:
        """Generate the weather SVG file."""
        try:
            # Get current date info
            today = pendulum.now()
            today_day = today.format("dddd")
            
            # Calculate time since graduation
            grad_date = pendulum.parse(self.grad_date)
            ps_time = pendulum.instance(today).diff_for_humans(grad_date, absolute=True)
            
            # Fetch weather data
            deg_f, deg_c, icon_url = self.fetch_weather(self.latitude, self.longitude)
            weather_emoji = self.get_weather_emoji(icon_url)
            
            # Read template
            template_path = self.template_path
            if not template_path.is_absolute():
                template_path = Path(__file__).parent / template_path
                
            template_content = template_path.read_text(encoding="utf-8")
            
            # Replace placeholders
            output_content = template_content.replace("{degF}", str(deg_f))
            output_content = output_content.replace("{degC}", str(deg_c))
            output_content = output_content.replace("{weatherEmoji}", weather_emoji)
            output_content = output_content.replace("{psTime}", ps_time)
            output_content = output_content.replace("{todayDay}", today_day)
            output_content = output_content.replace(
                "{dayBubbleWidth}", 
                str(self.DAY_BUBBLE_WIDTHS[today_day])
            )
            
            # Write output
            output_path = self.output_path
            if not output_path.is_absolute():
                output_path = Path(__file__).parent / output_path
                
            output_path.write_text(output_content, encoding="utf-8")
            
            print(f"✅ Successfully generated {output_path}")
            print(f"🌡️  Temperature: {deg_f}°F ({deg_c}°C)")
            print(f"☁️  Condition: {weather_emoji}")
            
        except requests.exceptions.RequestException as err:
            print(f"❌ Error fetching weather data: {err}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError as err:
            print(f"❌ File not found: {err}", file=sys.stderr)
            sys.exit(1)
        except Exception as err:
            print(f"❌ Unexpected error: {err}", file=sys.stderr)
            sys.exit(1)




if __name__ == "__main__":
    CliApp.run(App)
