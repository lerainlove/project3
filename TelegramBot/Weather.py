import requests
# Читаем наш ключ из отдельного файла
API_KEY = open("../data/API_KEY.txt").read()

def make_query(lat, lon, hourly = False, daily = False):
    if not (hourly ^ daily):
        raise Exception("Only one type available")
    global API_KEY

    # Делаем запрос к локации
    location = requests.get(
        f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={lat}%2C{lon}"
    )

    # Если запрос был выполнен успешно, получаем погоду на острове
    if location.status_code == 200:
       json_location = location.json()
       if json_location is None: return None

       location_key = json_location["Key"]

       if hourly:
            result = requests.get(
                f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}?apikey={API_KEY}&details=true&metric=true"
            )
            return result.json() if result.status_code == 200 else result.status_code
       elif daily:
            result = requests.get(
                f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={API_KEY}&details=true&metric=true"
            )
            return result.json()["DailyForecasts"] if result.status_code == 200 else result.status_code
    else:
        return location.status_code

# Возвращает саммари для часовых запросов
def summary_hourly(cell):
    result = [
            f"Температура: {round(cell['Temperature']['Value'],1)}°C",
            f"Ощущается как: {round(cell['RealFeelTemperature']['Value'],1)}°C",
            f"Скорость ветра: {round(cell['Wind']['Speed']['Value'],2)} км/ч",
            f"Вероятность дождя: {round(cell['RainProbability'],2)} %",
        ]

    return '\n'.join(result), cell["Link"]

# Возвращает саммари для запросов по дням
def summary_daily(cell):
    tmp = {
        "Средняя температура": round((cell["Temperature"]["Minimum"]["Value"] + cell["Temperature"]["Maximum"]["Value"])/2,1),
        "Ощущается как": round((cell["RealFeelTemperature"]["Minimum"]["Value"] + cell["RealFeelTemperature"]["Maximum"]["Value"])/2,1),
        "Скорость ветра": round(cell["Day"]["Wind"]["Speed"]["Value"],2),
        "Вероятность дождя": round(cell["Day"]["RainProbability"],2),
    }
    result = [
        f"Средняя температура: {tmp['Средняя температура']}°C",
        f"Ощущается как: {tmp['Ощущается как']}°C",
        f"Скорость ветра: {tmp['Скорость ветра']} км/ч",
        f"Вероятность дождя: {tmp['Вероятность дождя']} %"
    ]

    return '\n'.join(result), cell["Link"]
