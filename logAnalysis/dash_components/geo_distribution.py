import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from dash import html, dcc
from ..models import ServerLog  # Relative import

def create_geo_distribution_app():
    """Creates and returns the configured geographic distribution Dash app"""
    
    # Initialize the app
    app = DjangoDash('WebLogMap', external_scripts=["https://cdn.plot.ly/plotly-2.18.2.min.js"])

    # Country configuration
    COUNTRY_PREFIXES = {
        "168.": "Botswana",
        "102.": "South Africa",
        "154.": "Namibia",
        "197.": "Zimbabwe"
    }

    ISO_MAP = {
        "Botswana": "BWA",
        "South Africa": "ZAF",
        "Namibia": "NAM",
        "Zimbabwe": "ZWE"
    }

    def process_log_data():
        """Processes log data and returns visualization dataframe"""
        country_counts = {country: 0 for country in ISO_MAP.keys()}
        invalid_count = 0

        for log in ServerLog.objects.all():
            ip_str = str(log.ip_address).strip() if log.ip_address else ""
            matched = False
            
            for prefix, country in COUNTRY_PREFIXES.items():
                if ip_str.startswith(prefix):
                    country_counts[country] += 1
                    matched = True
                    break
            
            if not matched and ip_str:
                print(f"Unmatched IP: {ip_str}")
                invalid_count += 1

        print(f"Processed logs - Valid: {sum(country_counts.values())}, Invalid/Unmatched: {invalid_count}")

        return pd.DataFrame({
            "country": list(country_counts.keys()),
            "logs": list(country_counts.values()),
            "iso_alpha": [ISO_MAP[country] for country in country_counts.keys()]
        })

    def create_map_figure():
        """Creates the choropleth map figure"""
        df = process_log_data()
        
        fig = px.choropleth(
            df,
            locations="iso_alpha",
            color="logs",
            hover_name="country",
            color_continuous_scale="Blues",
            scope="africa"
        )

        fig.update_geos(
            projection_type="mercator",
            center={"lat": -25, "lon": 25},
            projection_scale=4,
            showcountries=True,
            countrycolor="Black"
        )

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar={
                "title": "Log Count",
                "thickness": 20,
                "len": 0.5
            }
        )
        
        return fig

    # Set the app layout
    app.layout = html.Div([
        dcc.Graph(
            id='geo-distribution-map',
            figure=create_map_figure(),
            style={'height': '200px', 'width': '240px'}
        )
    ])

    return app
