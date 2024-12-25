<h1>Описание проекта и его составляющих</h1>

# 1 Директория  `data`
Здесь содержатся текстовые файлы, в которых лежат ключи для подключения к API AccuWeather

В `API_KEY.txt` лежит ключ, который используется сейчас, в `extra_keys.txt` ключи, которые используются, когда кончилось
количество запросов исходного ключа(для разработчиков)

# 2 Директория `templates`
Тут лежат html-файлы, которые используются в нашем проекте.  
* `index.html` - главная страница, куда можно ввести координаты запроса

# 3 api_queries.py
Здесь содержится все взаимодействие с API AccuWeather, которые используется
для получения данных для приложения(не Telegram-бота)

# 4 requirements.txt
Здесь находится список библиотек, необходимых для корректной работы проекта.

# 5 charts.py
Содержит функционал, который создает layout для графиков по датафреймам

# 6 main.py
Содержит основной функционал приложения. Здесь создается `Flask`-приложение
 и `Dash`-приложение.

Здесь реализовано получение точек из `index.html`, их обработка 
и переход на страницу с отображением графиков для этих точек.

# 7 Директория TelegramBot
> # 7.1 data
> * `API_KEY.txt` - ключ для подключения к API Telegram
> * `help.txt` - текст для сообщения команды `/help`
> * `start.txt` - текст для сообщения команды `/start`
>
> # 7.2 Telegram.py
> Содержится весь функционал бота. Обработка текста, команд и т.д.
> 
> # 7.3 Weather.py
> Функционал API AccuWeather для корректной работы бота