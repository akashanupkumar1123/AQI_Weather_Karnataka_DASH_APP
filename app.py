import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import page_container
from cache_config import cache

# = Initialize Dash App =
app = dash.Dash(
    __name__,
    use_pages=True,  # Enable Dash pages system
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]  # Use Bootstrap theme for styling
)
server = app.server
app.title = "Karnataka AQI Analyzer"  # Set the app title for browser tab

# = Cache Setup =
cache.init_app(server, config={
    'CACHE_TYPE': 'SimpleCache',  # Simple in-memory cache
    'CACHE_DEFAULT_TIMEOUT': 300  # Cache timeout in seconds
})

# = Navbar =
navbar = dbc.NavbarSimple(
    brand="🌫 Karnataka AQI Analyzer",
    brand_href="/",  # Link to home page on brand click
    brand_style={"fontSize": "1.5rem", "fontWeight": "bold", "color": "#00ffe1"},
    color="dark",
    dark=True,
    fluid=True,
    className="mb-4 shadow",
    children=[
        dbc.NavItem(dbc.NavLink("🔮 Predictor", href="/")),
        dbc.NavItem(dbc.NavLink("🌆 City Snapshot", href="/city-snapshot")),
        dbc.NavItem(dbc.NavLink("📈 Trends", href="/trends")),
        dbc.NavItem(dbc.NavLink("ℹ️ About", href="/about")),
    ],
    style={"zIndex": 1024},  # Ensure navbar z-index above other elements
)

# = Main Layout =
app.layout = html.Div([
    # Particle Background Canvas placeholder
    html.Div(id="particles-js"),
    
    # Inject custom favicon, CSS, and JS assets
    html.Link(rel="icon", type="image/x-icon", href="/assets/favicon.ico"),
    html.Link(rel="stylesheet", href="/assets/style.css"),
    html.Script(src="/assets/script.js"),
    html.Script(src="/assets/particles.min.js"),
    
    # Navbar component
    navbar,
    
    # Page content container wrapped with a loading spinner
    dcc.Loading(
        page_container,
        type="circle",
        color="#00ffe1",
        className="page-loading"
    )
], style={
    "minHeight": "100vh",
    # Do NOT set backgroundColor here to allow CSS gradient from style.css to show correctly
    "position": "relative",
    "zIndex": 1,
    "color": "#ffffff",  # Set text color white for dark theme
    "paddingBottom": "2rem",
    "fontFamily": "Segoe UI, sans-serif"
})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
