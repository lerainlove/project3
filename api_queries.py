import requests
import pandas as pd

API_SECRET = open("data/API_KEY.txt").read()


def fetch_weather_data(location_response, is_hourly=False, is_daily=False):
    if is_hourly == is_daily:
        raise ValueError("Specify exactly one type: hourly or daily.")

    if location_response.status_code == 200:
        location_data = location_response.json()
        location_id = location_data["Key"]

        if is_hourly:
            response = requests.get(
                f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_id}?apikey={API_SECRET}&details=true&metric=true"
            )
            return response.json()

        if is_daily:
            response = requests.get(
                f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_id}?apikey={API_SECRET}&details=true&metric=true"
            )
            return response.json().get("DailyForecasts", [])

    else:
        print(f"Failed API request with status code: {location_response.status_code}")
        return None


def extract_hourly_data(json_data, waypoint, index):
    location_label = "Start Point" if waypoint == "start" else \
                     "End Point" if waypoint == "finish" else \
                     f"Additional Point {index}"

    data_frame = pd.DataFrame({
        "Time": [],
        "Temperature": [],
        "Wind Speed": [],
        "Precipitation Probability": [],
        "Location": []
    })

    for record in json_data:
        row = pd.DataFrame({
            "Time": [':'.join(record["DateTime"].split(':')[:2])],
            "Temperature": record["Temperature"]["Value"],
            "Wind Speed": record["Wind"]["Speed"]["Value"],
            "Precipitation Probability": record["RainProbability"],
            "Location": [location_label]
        })
        data_frame = pd.concat((data_frame, row))

    return data_frame


def extract_daily_data(json_data, waypoint, index):
    location_label = "Start Point" if waypoint == "start" else \
                     "End Point" if waypoint == "finish" else \
                     f"Additional Point {index}"

    data_frame = pd.DataFrame({
        "Time": [],
        "Temperature": [],
        "Wind Speed": [],
        "Precipitation Probability": [],
        "Location": []
    })

    for record in json_data:
        avg_temp = (record["Temperature"]["Minimum"]["Value"] + record["Temperature"]["Maximum"]["Value"]) / 2
        row = pd.DataFrame({
            "Time": [':'.join(record["Date"].split(':')[:2])],
            "Temperature": avg_temp,
            "Wind Speed": record["Day"]["Wind"]["Speed"]["Value"],
            "Precipitation Probability": record["Day"]["RainProbability"],
            "Location": [location_label]
        })
        data_frame = pd.concat((data_frame, row))

    return data_frame


def process_locations(locations_list, waypoint):
    hourly_data = pd.DataFrame({
        "Time": [],
        "Temperature": [],
        "Wind Speed": [],
        "Precipitation Probability": [],
        "Location": [],
    })

    daily_data = hourly_data.copy()

    for idx, coordinates in enumerate(locations_list, start=1):
        latitude = coordinates["lat"]
        longitude = coordinates["lon"]

        location_response = requests.get(
            f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={API_SECRET}&q={latitude}%2C{longitude}"
        )

        hourly_forecast = fetch_weather_data(location_response, is_hourly=True)
        daily_forecast = fetch_weather_data(location_response, is_daily=True)

        if hourly_forecast:
            hourly_data = pd.concat((hourly_data, extract_hourly_data(hourly_forecast, waypoint, idx)))
        if daily_forecast:
            daily_data = pd.concat((daily_data, extract_daily_data(daily_forecast, waypoint, idx)))

    return hourly_data, daily_data


if __name__ == "__main__":
    waypoints = {
        "start": [{"lat": 45, "lon": 50}],
        "extra": [
            {"lat": 48, "lon": 50},
            {"lat": 52, "lon": 50}
        ],
        "finish": [{"lat": 55, "lon": 50}]
    }

    start_hourly, start_daily = process_locations(waypoints["start"], "start")
    extra_hourly, extra_daily = process_locations(waypoints["extra"], "extra")
    finish_hourly, finish_daily = process_locations(waypoints["finish"], "finish")

    combined_hourly = pd.concat((start_hourly, extra_hourly, finish_hourly))
    combined_daily = pd.concat((start_daily, extra_daily, finish_daily))

