from django_plotly_dash import DjangoDash
from dash import html, dcc, Input, Output
from django.db.models import Count
from django.db.models.functions import ExtractYear
from ..models import ServerLog

def create_dropdown_app():
    """Creates and returns a Dash app for the global year dropdown"""
    app = DjangoDash('YearDropdown')

    def get_years():
        """Fetch distinct years from ServerLog timestamps"""
        years = ServerLog.objects.annotate(
            year=ExtractYear('timestamp')
        ).values('year').distinct().order_by('year')
        return [year['year'] for year in years]

    # Get available years
    years = get_years()
    year_options = [{'label': 'All', 'value': 'All'}] + [{'label': str(year), 'value': str(year)} for year in years]

    # Layout with dropdown and store
    app.layout = html.Div([
        dcc.Dropdown(
            id='global-year-dropdown',
            options=year_options,
            value='All',
            clearable=False,
            style={'width': '100%', 'height':'20px'}
        ),
        dcc.Store(id='global-year-store', data='All')  # Store to share state
    ])

    # Callback to update store
    @app.callback(
        Output('global-year-store', 'data'),
        Input('global-year-dropdown', 'value')
    )
    def update_store(selected_year):
        return selected_year

    return app