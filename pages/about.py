import dash
from dash import html, Output, Input, dcc
import dash_bootstrap_components as dbc
from mlflow_utils import list_experiments, get_latest_mlflow_stats

# Register this file as a Dash page with path "/about"
dash.register_page(__name__, path='/about', name='ℹ️ About')

layout = html.Div(
    style={"padding": "2rem", "maxWidth": "900px", "margin": "auto"},
    children=[
        html.H2("ℹ️ About This AQI App", className="text-center mb-3"),
        html.P(
            "This dashboard is a modern, AI-powered air quality forecasting tool for Karnataka cities. "
            "It combines LSTM-based time series prediction and LightGBM classification, with MLflow managing experiment logs.",
            className="text-center", style={"opacity": 0.85}
        ),
        html.Hr(),
        # Interval to load MLflow summary once after page load
        dcc.Interval(id="load-mlflow", interval=1, n_intervals=0, max_intervals=1),
        # Container to display MLflow experiment summaries
        html.Div(id="mlflow-content", className="mt-4"),
        html.Hr(),
        html.Div([
            html.P("🧑‍💻 Created with ❤️ by Akash Anupkumar"),
            html.P("🔗 Powered by Python, Dash, MLflow, TensorFlow, LightGBM"),
        ], style={
            "textAlign": "center",
            "fontStyle": "italic",
            "marginTop": "30px",
            "opacity": 0.8
        })
    ]
)

@dash.callback(
    Output("mlflow-content", "children"),
    Input("load-mlflow", "n_intervals")
)
def load_mlflow_summary(n):
    # Fetch list of MLflow experiments
    experiments = list_experiments()
    if not experiments:
        # Show warning if no experiments found
        return html.Div("⚠️ No MLflow experiments found.", style={"color": "red", "textAlign": "center"})

    cards = []
    for exp_name in experiments:
        # Get latest run stats for each experiment
        exp, run_id, metrics, params = get_latest_mlflow_stats(exp_name)

        # Prepare metric and parameter lists
        metric_list = [
            html.Li(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
            for k, v in metrics.items()
        ]
        param_list = [
            html.Li(f"{k}: {v}")
            for k, v in params.items()
        ]

        # Construct a card displaying experiment details
        card = dbc.Card([
            dbc.CardHeader(html.H5(f"📦 Experiment: {exp}")),
            dbc.CardBody([
                html.P(f"🆔 Run ID: {run_id}", style={"fontSize": "0.9em", "color": "#555"}),
                html.H6("📊 Metrics", className="mt-3"),
                html.Ul(metric_list or [html.Li("No metrics available")]),
                html.H6("⚙️ Parameters", className="mt-3"),
                html.Ul(param_list or [html.Li("No parameters available")])
            ])
        ], className="mb-4 shadow-sm")
        cards.append(card)

    return cards
