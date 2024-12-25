import pandas as pd
from flask import Flask, request, render_template, redirect
from dash import Dash
from api_queries import get_hourly_daily_list
from charts import create_weather_dashboard
from dash.dependencies import Input, Output
import plotly.express as px
from flask import Flask, request, redirect, render_template
from dash import Dash, Input, Output
import pandas as pd
import plotly.express as px

# Flask сервер
app = Flask(__name__)

# Dash приложение
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')

# Данные о погоде
weather_data_hourly = None
weather_data_daily = None

# Пустой layout для инициализации
empty_dataframe = pd.DataFrame({
    "Time": [],
    "Temperature": [],
    "Wind Speed": [],
    "Rain Probability": [],
    "Location": []
})
dash_app.layout = create_weather_dashboard(empty_dataframe, empty_dataframe)


# Обновление графика на основе пользовательского ввода
@dash_app.callback(
    Output('weather-graph', 'figure'),
    [Input('location-selector', 'value'),
     Input('time-selector', 'value'),
     Input('category-selector', 'value')]
)
def update_weather_chart(selected_location, time_period, category):
    global weather_data_hourly, weather_data_daily

    if weather_data_hourly is None or weather_data_daily is None:
        return {}

    # Выбор датафрейма в зависимости от временного периода
    if time_period == 5:  # 5 дней
        data_frame = weather_data_daily
        filtered_data = data_frame[data_frame['Location'] == selected_location].copy()
        period_description = "5 дней"
    else:
        data_frame = weather_data_hourly
        filtered_data = data_frame[data_frame['Location'] == selected_location].copy()
        filtered_data = filtered_data.iloc[-time_period:]
        period_description = f"{time_period} часа" if time_period == 3 else f"{time_period} часов"

    # Построение графика
    figure = px.line(
        filtered_data,
        x='Time',
        y=category,
        title=f'{category} - {selected_location} - Последние {period_description}',
        markers=True
    )

    # Настройка осей графика
    y_axis_config = dict(
        showgrid=True,
        gridcolor='lightgrey',
        gridwidth=1
    )

    if category == "Wind Speed":
        y_axis_config.update(range=[0, None])
    elif category == "Rain Probability":
        y_axis_config.update(range=[0, 100])

    figure.update_layout(
        xaxis_title="Время",
        yaxis_title=category,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgrey',
            gridwidth=1
        ),
        yaxis=y_axis_config
    )

    return figure


# Получение координат из формы
def extract_points_from_form():
    coordinates = {
        'start': [{
            'lat': float(request.form['start-latitude']),
            'lon': float(request.form['start-longitude'])
        }],
        'finish': [{
            'lat': float(request.form['finish-latitude']),
            'lon': float(request.form['finish-longitude'])
        }],
        'extra': []
    }

    for idx in range(1, 9):
        lat_key = f'extra-latitude-{idx}'
        lon_key = f'extra-longitude-{idx}'

        if lat_key in request.form and lon_key in request.form:
            if request.form[lat_key] and request.form[lon_key]:
                coordinates['extra'].append({
                    'lat': float(request.form[lat_key]),
                    'lon': float(request.form[lon_key])
                })

    return coordinates


@app.route('/', methods=['GET', 'POST'])
def home():
    global weather_data_hourly, weather_data_daily

    if request.method == 'POST':
        # Извлекаем координаты из формы
        points = extract_points_from_form()

        # Получение данных о погоде
        start_hourly, start_daily = get_hourly_daily_list(points['start'], "start")
        extra_hourly, extra_daily = get_hourly_daily_list(points['extra'], "extra")
        finish_hourly, finish_daily = get_hourly_daily_list(points['finish'], "finish")

        # Объединение данных
        weather_data_hourly = pd.concat([start_hourly, extra_hourly, finish_hourly])
        weather_data_daily = pd.concat([start_daily, extra_daily, finish_daily])

        # Обновление Dash layout
        dash_app.layout = create_weather_dashboard(weather_data_hourly, weather_data_daily)

        return redirect('/dashboard/')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=8050)

