from dash import dcc, html
from dash.dependencies import Input, Output

def create_metric_dropdown(app, default_value='GDP'):
    """Create a standalone metric dropdown component"""
    
    # Define the dropdown options
    options = [
        {'label': 'GDP', 'value': 'GDP'},
        {'label': 'Population', 'value': 'Population'}
    ]
    
    # Create the dropdown component
    dropdown = dcc.Dropdown(
        id='metric-dropdown',
        options=options,
        value=default_value,
        clearable=False
    )
    
    # Wrap in a Div with label for better presentation
    component = html.Div([
        html.Label("Select Metric:"),
        dropdown
    ], style={'width': '30%', 'margin': '20px auto'})
    
    return component

def register_metric_dropdown_callbacks(app):
    """Register any callbacks needed for the dropdown"""
    # This dropdown is simple and doesn't need its own callbacks
    # Callbacks would be registered in the main app
    pass