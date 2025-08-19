import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import base64
import os
import pandas as pd
from tensorflow.keras.models import load_model
from utils import fetch_live_weather, get_latest_data_for_lstm, predict_category, fetch_live_aqi_aqicn

# Register this file as a Dash page with path "/city-snapshot"
dash.register_page(__name__, path='/city-snapshot', name='🌆 City Snapshot')

# Default pollutant values per city (can be adapted if you have live data)
CITY_FEATURE_DEFAULTS = {
    "Bangalore": {"pm2.5": 35.0, "co": 0.9, "pm10": 60.0, "no2": 20.0, "o3": 40.0, "so2": 14.0},
    "Mysore":    {"pm2.5": 25.0, "co": 0.7, "pm10": 40.0, "no2": 14.0, "o3": 30.0, "so2": 8.0}
}

def load_plot_content(city):
    """Load city-specific AQI plot image and encode to base64 for inline display."""
    file_map = {
        "Bangalore": "assets/plots/bangalore_aqi_plot.png",
        "Mysore": "assets/plots/mysuru_aqi_plot.png"
    }
    path = file_map.get(city)
    if not path or not os.path.exists(path):
        return None, None  # No plot available
    
    with open(path, "rb") as f:
        b64_bytes = base64.b64encode(f.read()).decode()
    return "image", b64_bytes

def layout():
    """Define the layout for the City Snapshot page."""
    return html.Div([
        html.H2("🌆 City Snapshot: Weather, AQI & Forecast", className="text-center mb-4"),
        html.P(
            "Live weather updates and AQI forecast based on real-time sensor input.",
            className="text-center", style={"opacity": 0.8}
        ),
        # Interval component to refresh weather data every 5 minutes
        dcc.Interval(id="refresh-weather", interval=5 * 60 * 1000, n_intervals=0),
        # Weather cards container for multiple cities
        html.Div(id="weather-cards", className="d-flex flex-wrap justify-content-center gap-3 mb-4"),
        html.Div([
            html.Div([
                html.Label("🏙 Select City", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="city-plot-dropdown",
                    options=[
                        {"label": "Bangalore", "value": "Bangalore"},
                        {"label": "Mysore", "value": "Mysore"}
                    ],
                    value="Bangalore",
                    className="dropdown"
                )
            ], style={"maxWidth": "300px", "margin": "0 auto"}),
            # Display live AQI and category for the selected city
            html.Div(id="forecasted-aqi", className="text-center my-3", style={"fontSize": "1.3rem"}),
            # Display AQI plot image for the selected city
            html.Div(id="city-aqi-image", className="text-center mt-3")
        ])
    ], style={"padding": "2rem"})

@dash.callback(
    Output("weather-cards", "children"),
    Output("city-aqi-image", "children"),
    Output("forecasted-aqi", "children"),
    Input("refresh-weather", "n_intervals"),
    Input("city-plot-dropdown", "value")
)
def update_city_snapshot(n, selected_city):
    # --- 1. Weather Cards for All Cities ---
    city_list = ["Bangalore", "Mysore"]
    cards = []
    for city in city_list:
        w = fetch_live_weather(city=city)
        weather_card = dbc.Card([
            dbc.CardHeader(html.H4(f"📍 {city}")),
            dbc.CardBody([
                # Static weather icon for simplicity; can be updated dynamically
                html.Img(
                    src="https://cdn.weatherapi.com/weather/64x64/day/116.png",
                    style={"height": "48px"}
                ),
                html.P(f"🌡 Temperature: {w.get('temp', '--')} °C"),
                html.P(f"💧 Humidity: {w.get('humidity', '--')}%"),
                html.P(f"💨 Wind: {w.get('wind', '--')} kph"),
                html.P(f"☁️ Condition: {w.get('description', '--')}"),
            ])
        ], color="light", outline=True, className="m-2", style={
            "width": "18rem", "boxShadow": "0 4px 8px rgba(0,0,0,0.1)", "borderRadius": "12px"
        })
        cards.append(weather_card)

    # --- 2. Live AQI and Category for Selected City ---
    try:
        live_aqi = fetch_live_aqi_aqicn()
        if live_aqi is None:
            live_aqi_display = "Unavailable"
            category = "Unknown"
        else:
            live_aqi_display = live_aqi
            category = predict_category(pd.DataFrame([[live_aqi]], columns=["AQI"]))
        pred_text = html.Div(
            f"🌍 Live AQI: {live_aqi_display}  🧠 Category: {category}",
            style={"fontWeight": "bold"}
        )
    except Exception as e:
        pred_text = html.Div(f"❌ Live AQI unavailable: {str(e)}", style={"color": "red"})

    # --- 3. Plot rendering for selected city ---
    plot_type, plot_content = load_plot_content(selected_city)
    if plot_type == "image":
        image = html.Img(
            src=f"data:image/png;base64,{plot_content}",
            style={
                "width": "100%", "maxWidth": "720px", "margin": "auto", "display": "block",
                "borderRadius": "16px", "boxShadow": "0 4px 20px rgba(0,0,0,0.25)"
            },
            alt=f"{selected_city} AQI Plot"
        )
    else:
        image = html.P("❌ Plot not available for this city.", style={"color": "gray", "textAlign": "center"})

    return cards, image, pred_text
