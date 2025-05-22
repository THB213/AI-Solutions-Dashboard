"""
URL configuration for WebAnalysisTool project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from logAnalysis.views import stream_logs, dashboard,upload_logs, dashboard_view1, Salesdashboard, NewDashboard, RegionalSalesAnalysis
from dash_app.views import dashboard_view
from dash_app.dash_apps import app  # Import your Dash app file
from logAnalysis.dash_apps import  geo_distribution_app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logs/', stream_logs, name='stream_logs'),
    path('dashboard/', dashboard, name='dashboard'),
    path("upload/", upload_logs, name="upload_logs"),
    path("dashboard_test/", dashboard_view, name="dashboard_test"),
    path("django_plotly_dash/", include("django_plotly_dash.urls")),
    path('dashboard1/', dashboard_view1, name='dashboard1'),
    path('SalesDashboard/', Salesdashboard, name='SalesDashboard'),
    path("Overview/", NewDashboard, name='Overview'),
    path('RegionalSalesAnalysis/', RegionalSalesAnalysis, name='RegionalSalesAnalysis'),


]

