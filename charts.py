from dash import dcc, html

# Отображение графиков по 2 датафреймам(для часов и дней)
def create_weather_dashboard(hourly_df, daily_df):
    hourly_df = hourly_df.copy()
    daily_df = daily_df.copy()

    # На графике ось скорости ветра будет начинаться от 0
    # На графике вероятности дождя всегда ордината будет между 0 и 100
    for df in [hourly_df, daily_df]:
        df['Ветер'] = df['Ветер'].clip(lower=0)
        df['Вероятность осадков'] = df['Вероятность осадков'].clip(lower=0, upper=100)

    # Получаем список локаций, создаем категории для показа графиков
    locations = hourly_df['Location'].unique().tolist()
    categories = ["Ветер", "Температура", "Вероятность осадков"]

    # Делаем layout
    layout = html.Div([
        # Название по центру
        html.H1("Погодные условия",
                style={'textAlign': 'center', 'margin': '20px'}),

        # Сам график
        dcc.Graph(id='weather-graph'),

        # Контейнер для кнопок
        html.Div([
            # Кнопки для локаций
            html.Div([
                html.H4("Локации", style={'margin': '10px'}),
                html.Div([
                    dcc.RadioItems(
                        id='location-selector',
                        options=[{'label': loc, 'value': loc} for loc in locations],
                        value=locations[0] if locations else None,
                        labelStyle={'display': 'block', 'margin': '10px'},
                        style={'display': 'inline-block'}
                    )
                ])
            ], style={'flex': '1', 'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '10px',
                      'margin': '10px'}),

            # Кнопки для Временных интервалов
            html.Div([
                html.H4("Временной период", style={'margin': '10px'}),
                html.Div([
                    dcc.RadioItems(
                        id='time-selector',
                        options=[
                            {'label': '3 часа', 'value': 3},
                            {'label': '12 часов', 'value': 12},
                            {'label': '5 дней', 'value': 5}
                        ],
                        value=3,
                        labelStyle={'display': 'block', 'margin': '10px'},
                        style={'display': 'inline-block'}
                    )
                ])
            ], style={'flex': '1', 'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '10px',
                      'margin': '10px'}),

            # Кнопки для типа графика(температура, скорость ветра, вероятность дождя)
            html.Div([
                html.H4("Категории", style={'margin': '10px'}),
                html.Div([
                    dcc.RadioItems(
                        id='category-selector',
                        options=[{'label': cat, 'value': cat} for cat in categories],
                        value='Температура',
                        labelStyle={'display': 'block', 'margin': '10px'},
                        style={'display': 'inline-block'}
                    )
                ])
            ], style={'flex': '1', 'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '10px',
                      'margin': '10px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '20px'})
    ])

    return layout
