import dash
from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import (
    predict_future_aqi,
    predict_category,
    get_latest_data_for_lstm
)

# Register this file as a Dash page with path "/"
dash.register_page(name, path="/", name="🔮 Predictor")

# Feature and label definitions for pollutant inputs
FEATURE_NAMES = ["pm2.5", "co", "pm10", "no2", "o3", "so2"]
LABELS = {
    "pm2.5": "🌫 PM2.5 (µg/m³)",
    "co": "🛢 CO (mg/m³)",
    "pm10": "🌁 PM10 (µg/m³)",
    "no2": "🧪 NO2 (µg/m³)",
    "o3": "🌐 Ozone (µg/m³)",
    "so2": "🔥 SO2 (µg/m³)"
}
# Predefined pollutant concentration ranges for dropdown options
POLLUTANT_RANGES = {
    "pm2.5": [round(x, 1) for x in np.arange(0.1, 100.1, 2.5)],
    "co": [round(x, 2) for x in np.arange(0.1, 5.1, 0.1)],
    "pm10": [round(x, 1) for x in np.arange(0.1, 200.1, 5.0)],
    "no2": [round(x, 1) for x in np.arange(0.1, 100.1, 2.5)],
    "o3": [round(x, 1) for x in np.arange(0.1, 200.1, 2.5)],
    "so2": [round(x, 1) for x in np.arange(0.1, 80.1, 2.5)]
}

def pollutant_dropdown(id, label, options, placeholder):
    """Construct a dropdown with manual numeric input for pollutant value."""
    return html.Div([
        html.Label(label),
        dcc.Dropdown(
            id=id,
            options=[{"label": f"{v:.2f}" if isinstance(v, float) else str(v), "value": v} for v in options],
            placeholder=placeholder,
            clearable=True,
            searchable=True,
            style={"marginBottom": "8px"},
            persistence=True
        ),
        dcc.Input(
            id=f"{id}-manual",
            type="number",
            placeholder="Or enter custom value",
            className="form-control",
            step="any",  # Allow decimal inputs
            style={
                "marginBottom": "18px",
                "color": "#da1b1b",       # Red input text
                "borderColor": "#da1b1b", # Red border
                "boxShadow": "0 0 0 1px #da1b1b"
            }
        ),
    ])

# Layout for the AQI Predictor page
layout = dbc.Container([
    html.H2("🔮 AQI Predictor - Forecast Karnataka's Air Quality", className="text-center mb-4"),
    dbc.Card([
        dbc.CardHeader("🧪 Enter Pollutant Levels & Prediction Window"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    pollutant_dropdown("input-pm25", LABELS["pm2.5"], POLLUTANT_RANGES["pm2.5"], "Select PM2.5"),
                    pollutant_dropdown("input-co", LABELS["co"], POLLUTANT_RANGES["co"], "Select CO"),
                    pollutant_dropdown("input-pm10", LABELS["pm10"], POLLUTANT_RANGES["pm10"], "Select PM10")
                ], md=4),
                dbc.Col([
                    pollutant_dropdown("input-no2", LABELS["no2"], POLLUTANT_RANGES["no2"], "Select NO2"),
                    pollutant_dropdown("input-o3", LABELS["o3"], POLLUTANT_RANGES["o3"], "Select Ozone"),
                    pollutant_dropdown("input-so2", LABELS["so2"], POLLUTANT_RANGES["so2"], "Select SO2")
                ], md=4),
                dbc.Col([
                    html.Label("⏱ Hours to Predict Ahead:", style={"fontWeight": "bold"}),
                    dcc.Slider(
                        id="hours-ahead", min=1, max=24, step=1, value=6,
                        marks={i: str(i) for i in range(1, 25)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Br(),
                    dbc.Button("🔍 Predict AQI", id="predict-btn", color="primary", className="mt-3 w-100"),
                    html.Div(id="prediction-output", className="mt-4")
                ], md=4)
            ])
        ])
    ], className="mb-4"),
    html.Hr(style={"borderColor": "white"}),
    html.Div(id="aqi-line-graph"),
    html.Div(
        html.Img(
            src="/assets/plots/feature_importance.png",
            style={
                "width": "100%",
                "maxWidth": "960px",
                "margin": "32px auto 0 auto",
                "display": "block",
                "borderRadius": "16px",
                "boxShadow": "0 2px 22px rgba(0,0,0,0.21)"
            },
            alt="Feature Importance for Air Quality Model"
        ),
        className="text-center"
    ),
    html.Div(
        "Which pollutants most influence AQI prediction.",
        className="text-muted",
        style={"textAlign": "center", "marginBottom": "2rem"}
    )
], fluid=True)

@dash.callback(
    Output("prediction-output", "children"),
    Output("aqi-line-graph", "children"),
    Input("predict-btn", "n_clicks"),
    State("input-pm25", "value"), State("input-pm25-manual", "value"),
    State("input-co", "value"), State("input-co-manual", "value"),
    State("input-pm10", "value"), State("input-pm10-manual", "value"),
    State("input-no2", "value"), State("input-no2-manual", "value"),
    State("input-o3", "value"), State("input-o3-manual", "value"),
    State("input-so2", "value"), State("input-so2-manual", "value"),
    State("hours-ahead", "value")
)
def update_prediction(
    n_clicks,
    pm25, pm25_manual,
    co, co_manual,
    pm10, pm10_manual,
    no2, no2_manual,
    o3, o3_manual,
    so2, so2_manual,
    hours_ahead
):
    # Do nothing if prediction button not clicked
    if not n_clicks:
        return no_update, no_update

    # Helper to choose manual input if provided, else dropdown value
    def get_val(drop, manual):
        return manual if manual is not None else drop

    input_values = [
        get_val(pm25, pm25_manual),
        get_val(co, co_manual),
        get_val(pm10, pm10_manual),
        get_val(no2, no2_manual),
        get_val(o3, o3_manual),
        get_val(so2, so2_manual)
    ]

    # Require all pollutant values to be provided
    if any(v is None for v in input_values):
        return html.Div("⚠️ Please provide all pollutant values (pick from dropdown or enter custom).",
                        style={"color": "orange"}), no_update

    base_row = dict(zip(FEATURE_NAMES, input_values))
    
    try:
        # Prepare input array for LSTM model prediction
        X_lstm = get_latest_data_for_lstm(base_row)
        forecast = []
        # Predict AQI for requested hours ahead
        for _ in range(hours_ahead):
            pred = predict_future_aqi(X_lstm)
            if pred is None:
                raise ValueError("Prediction failed.")
            forecast.append(pred)
            # Note: no autoregressive input update in this model
        last_aqi = forecast[-1]
        category = predict_category(pd.DataFrame([[last_aqi]], columns=["AQI"]))
    except Exception as e:
        return html.Div(f"❌ Prediction error: {str(e)}", style={"color": "red"}), no_update

    # Construct line graph for AQI forecast
    graph = dcc.Graph(
        figure=go.Figure(
            data=[go.Scatter(y=forecast, mode='lines+markers', name='AQI Forecast')],
            layout=go.Layout(
                title=f"📈 AQI Forecast for Next {hours_ahead} Hours",
                xaxis_title="Hour",
                yaxis_title="Predicted AQI",
                template="plotly_dark"
            )
        )
    )
    # Display prediction summary and category
    summary = html.Div([
        html.H5(f"🌟 Forecasted AQI after {hours_ahead} hours: {last_aqi:.2f}", className="text-success"),
        html.H6(f"🧠 Predicted Category: {category}", className="text-info")
    ])
    return summary, graph
