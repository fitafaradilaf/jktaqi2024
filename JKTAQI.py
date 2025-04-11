import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Manually input the dataset
data = pd.DataFrame({
    'date': [
        '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
        '2024-02-01', '2024-02-02', '2024-02-03', '2024-02-04', '2024-02-05'
    ],
    'AQI': [120, 115, 130, 125, 89, 140, 135, 145, 151, 138],
    'traffic_congestion': [80, 85, 90, 88, 70, 95, 92, 100, 105, 98],
    'temperature': [30, 31, 29, 28, 27, 32, 33, 31, 30, 29],
    'wind_speed': [5, 6, 5, 4, 5, 7, 6, 5, 4, 5]
})

# Convert date column to datetime
data['date'] = pd.to_datetime(data['date'])

# Add AQI category and health implications
def classify_aqi(aqi):
    if 0 <= aqi <= 50:
        return "Good", "Green", "Air quality is considered satisfactory and poses little or no risk."
    elif 51 <= aqi <= 100:
        return "Moderate", "Yellow", "Acceptable air quality, but there may be a concern for some sensitive individuals."
    elif 101 <= aqi <= 150:
        return "Unhealthy for Sensitive Groups", "Orange", "People with respiratory conditions, children, and elderly may be affected."
    elif 151 <= aqi <= 200:
        return "Unhealthy", "Red", "Everyone may begin to experience health effects."
    elif 201 <= aqi <= 300:
        return "Very Unhealthy", "Purple", "Health alert: serious effects for everyone."
    elif 301 <= aqi <= 500:
        return "Hazardous", "Maroon", "Emergency conditions. Everyone should avoid outdoor exposure."
    else:
        return "Unknown", "Gray", "Invalid AQI value."

data[['AQI_Category', 'Color', 'Health_Implications']] = data['AQI'].apply(lambda x: pd.Series(classify_aqi(x)))

# Create the Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Jakarta AQI Dashboard (2024)", style={'textAlign': 'center'}),
    dcc.Graph(id='daily-aqi-chart'),
    dcc.Graph(id='line-chart'),
    html.Div(id='aqi-info', style={'textAlign': 'center', 'marginTop': '20px'}),
    dcc.Slider(
        id='date-slider',
        min=0,
        max=len(data) - 1,
        value=0,
        marks={i: str(data['date'].iloc[i].date()) for i in range(len(data))},
        step=1
    )
])

# Callback to update the charts and AQI information
@app.callback(
    [Output('daily-aqi-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('aqi-info', 'children')],
    [Input('date-slider', 'value')]
)
def update_chart(selected_index):
    # Get the selected date's data
    selected_data = data.iloc[selected_index]
    date = selected_data['date'].date()
    aqi = selected_data['AQI']
    category, color, implications = classify_aqi(aqi)
    temp = selected_data['temperature']
    wind = selected_data['wind_speed']

    # Create the bar chart
    bar_fig = px.bar(
        x=['AQI', 'Temperature', 'Wind Speed'],
        y=[aqi, temp, wind],
        labels={'x': 'Metric', 'y': 'Value'},
        title=f"Metrics for {date}",
        color_discrete_sequence=[color.lower()]
    )

    # Create the line chart for AQI trends
    line_fig = px.line(
        data,
        x='date',
        y='AQI',
        title='Daily AQI Trends in Jakarta (2024)',
        labels={'AQI': 'Air Quality Index', 'date': 'Date'},
        markers=True
    )
    line_fig.update_traces(line_color=color.lower())

    # AQI information
    info = html.Div([
        html.H3(f"Date: {date}"),
        html.H3(f"AQI: {aqi} ({category})", style={'color': color.lower()}),
        html.P(f"Health Implications: {implications}"),
        html.P(f"Temperature: {temp}°C"),
        html.P(f"Wind Speed: {wind} m/s")
    ])

    return bar_fig, line_fig, info

# Run the app
if __name__ == '__main__':
    app.run(debug=True)