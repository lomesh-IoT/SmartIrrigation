
from django.shortcuts import render
from django.http import JsonResponse
from .models import DHTData, PumpData, SoilMoistureData, MotionData
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from .serializers import MotionDataSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


# Variable to simulate pump state
pump_state = False  # False means off, True means on


def get_latest_sensor_data(request):
    # Retrieve data from the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    dht_data = DHTData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    soil_data = SoilMoistureData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    motion_data = MotionData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    pump_data = PumpData.objects.last()
    pump_status = pump_data.pumpStatus if pump_data else 'OFF'
    
    # Structure data for Chart.js
    response_data = {
        'temperature': [data.temperature for data in dht_data],
        'humidity': [data.humidity for data in dht_data],
        'soil_moisture': [data.moisture_level for data in soil_data],
        'motion': [1 if data.motion_detected else 0 for data in motion_data],
        'timestamps': [data.timestamp.strftime("%H:%M:%S") for data in dht_data],
        'pump_status': pump_status
    }
    return JsonResponse(response_data)

def get_data_for_dashboard(request):
    dht_data = DHTData.objects.last()
    temp = dht_data.temperature
    humid = dht_data.humidity
    soilData = SoilMoistureData.objects.last()
    soil_data = soilData.moisture_level
    latest_motion_data = MotionData.objects.last()
    serializer = MotionDataSerializer(latest_motion_data)
    print("Serializer =>",serializer)
    motionData = serializer.data
    print("motionData =>", motionData)
    motion_data = motionData["motion_detected"]
    print("motion_data =>", motion_data)
    pump_data = PumpData.objects.last()
    pump_status = pump_data.pumpStatus if pump_data else 'OFF'
    
    # Structure data for Chart.js
    response_data = {
        'temperature': temp,
        'humidity': humid,
        'soil_moisture': soil_data,
        'motion': motion_data,
        'pump_status': pump_status
    }
    return JsonResponse( response_data)

def chart(request):
    return render(request, 'sensors/charts.html')

def dashboard(request):
    return render(request, 'sensors/dashboard.html')

def get_pump_status(request):
    pump_data = PumpData.objects.last()
    pump_status = pump_data.pumpStatus if pump_data else 'OFF'
    return JsonResponse({'pump_status': pump_status})





