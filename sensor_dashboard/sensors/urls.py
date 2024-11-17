from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/data/', views.get_latest_sensor_data, name='get_latest_sensor_data'),
    path('board_data/', views.get_data_for_dashboard, name='get_data_for_dashboard'),
    path('charts/', views.chart, name='chart'),
    path('pump_status/', views.get_pump_status, name='get_pump_status'),

    # path('toggle_pump/', views.toggle_pump, name='toggle_pump'),
    # path('pump_control/', views.pump_control, name='pump_control'), 
]
