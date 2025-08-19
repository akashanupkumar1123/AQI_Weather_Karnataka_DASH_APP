import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Register this file as a Dash page with path "/trends"
dash.register_page(name, path='/trends', name='📈 Trends')

# Precomputed summaries and notable annotations for Bengaluru and Mysuru
SUMMARY_STATS = {
    "Bengaluru": {
        "avg_aqi": 78,
        "min_aqi": 32,
        "max_aqi": 151,
        "unhealthy_days": 5,
        "annotations": [
            "Diwali spike: Oct 2024, AQI 148",
            "Cleanest week: June 2025, avg AQI 40"
        ]
    },
    "Mysuru": {
        "avg_aqi": 65,
        "min_aqi": 30,
        "max_aqi": 120,
        "unhealthy_days": 2,
        "annotations": [
            "Winter peak: Jan 2025, AQI 118",
            "Lowest AQI: April 2025, AQI 33"
        ]
    }
}

# Map of cities to their historical AQI trend plot image paths
PLOT_MAP = {
    "Bengaluru": "/assets/plots/true_vs_predicted_aqi.png",
    "Mysuru": "/assets/plots/true_vs_predicted_aqi.png",
}

# AQI categories with ranges and colors for legend display
AQI_CATEGORIES = [
    ("Good", 0, 50, "#50f09c"),
    ("Satisfactory", 51, 100, "#a8f04f"),
    ("Moderate", 101, 200, "#ffe357"),
    ("Poor", 201, 300, "#ffb657"),
    ("Very Poor", 301, 400, "#ff8557"),
    ("Severe", 401, 500, "#fd3c3c"),
]

def _aqi_legend():
    """Construct AQI categories legend as a row of colored labels."""
    return dbc.Row([
        dbc.Col(html.Div("AQI Categories:"), width="auto"),
        *[
            dbc.Col(html.Div(
                style={
                    "display": "inline-block",
                    "background": color,
                    "borderRadius": "2px",
                    "padding": "0.3rem 0.7rem",
                    "marginRight": "0.6rem",
                    "fontWeight": "bold",
                    "color": "#1a1a1a" if idx < 3 else "#fff"
                },
                children=f"{label} ({lo}-{hi})"
            ), width="auto") for idx, (label, lo, hi, color) in enumerate(AQI_CATEGORIES)
        ]
    ], style={"marginTop": "0.7rem", "fontSize": "0.93rem"})

def layout():
    """Define layout for AQI Trends page with city selector, summary stats, trend image, and annotations."""
    return html.Div(
        style={"padding": "2rem"},
        children=[
            html.H2("📈 Karnataka AQI Trends", style={"textAlign": "center"}),
            html.P(
                "Long-term air quality patterns across Bengaluru and Mysuru—see category stats and narrative events below.",
                style={"textAlign": "center", "opacity": 0.88, "marginBottom": "1.9rem"}
            ),
            dbc.Card([
                dbc.CardBody([
                    html.Label("🏙 Select City", style={"fontWeight": "bold"}),
                    dcc.Dropdown(
                        id="city-dropdown",
                        options=[
                            {"label": "Bengaluru", "value": "Bengaluru"},
                            {"label": "Mysuru", "value": "Mysuru"}
                        ],
                        value="Bengaluru",
                        className="dropdown"
                    )
                ])
            ], className="card"),
            # Container for displaying summary statistics cards
            html.Div(id="summary-stats-row", className="mt-4"),
            # Container with loading spinner wrapping historical trend image
            dcc.Loading(
                html.Div(id="trend-image-container"),
                type="circle", color="white", className="mt-3"
            ),
            # AQI category legend displayed below the plot
            html.Div(_aqi_legend(), className="mt-4"),
            # Container for displaying city-specific narrative annotations or events
            html.Div(id="city-annotations", className="mt-3")
        ]
    )

@dash.callback(
    Output("trend-image-container", "children"),
    Output("summary-stats-row", "children"),
    Output("city-annotations", "children"),
    Input("city-dropdown", "value")
)
def update_trend_page(city):
    # Get and display the historical AQI trend image for selected city
    img_src = PLOT_MAP.get(city)
    if img_src:
        img_elem = html.Img(
            src=img_src,
            style={
                "width": "100%",
                "maxWidth": "720px",
                "margin": "0 auto",
                "display": "block",
                "borderRadius": "16px",
                "boxShadow": "0 1px 15px rgba(0,0,0,0.14)"
            },
            alt=f"{city} AQI Trend",
            title=f"{city} AQI Trend"
        )
    else:
        img_elem = html.Div("No plot available for this city.", style={"color": "red", "textAlign": "center"})

    # Create summary statistic cards for average, min, max AQI, and number of unhealthy days
    stats = SUMMARY_STATS.get(city)
    if stats:
        summary_row = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Avg AQI"),
                dbc.CardBody(html.H4(stats['avg_aqi'], className="text-success text-center"))
            ], className="text-center"), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Best (Min)"),
                dbc.CardBody(html.H4(stats['min_aqi'], className="text-primary text-center"))
            ], className="text-center"), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Worst (Max)"),
                dbc.CardBody(html.H4(stats['max_aqi'], className="text-danger text-center"))
            ], className="text-center"), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Unhealthy Days"),
                dbc.CardBody(html.H4(stats['unhealthy_days'], style={"color": "#ff924c"}, className="text-center"))
            ], className="text-center"), width=3),
        ], style={"marginBottom": "1rem", "justifyContent": "center"})
    else:
        summary_row = html.Div()

    # Display annotated narrative insights for the selected city
    annotations = stats.get("annotations", []) if stats else []
    facts = [dbc.Alert(anno, color="info", style={"marginBottom": "8px"}) for anno in annotations] if annotations else []
    facts_elem = html.Div(facts, style={"maxWidth": "600px", "margin": "0 auto"}) if facts else html.Div()

    return img_elem, summary_row, facts_elem
