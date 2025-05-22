from dash import html, dcc
from django_plotly_dash import DjangoDash

def create_country_filter():
    """Creates a standalone country filter dropdown component"""
    app = DjangoDash('CountryFilter')
    
    country_options = [
        {'label': 'All Countries', 'value': 'All'},
        {'label': 'Botswana', 'value': 'Botswana'},
        {'label': 'South Africa', 'value': 'South Africa'},
        {'label': 'Namibia', 'value': 'Namibia'},
        {'label': 'Zimbabwe', 'value': 'Zimbabwe'}
    ]
    
    app.layout = html.Div([
        dcc.Dropdown(
            id='country-filter',
            options=country_options,
            value='All',
            clearable=False,
            style={'width': '250px'}
        ),
        dcc.Store(id='filter-store', data='All')
    ])
    
    # Clientside callback to update the store
    app.clientside_callback(
        """
        function(country) {
            return country || 'All';
        }
        """,
        Output('filter-store', 'data'),
        Input('country-filter', 'value')
    )
    
    return app