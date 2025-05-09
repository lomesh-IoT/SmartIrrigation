
from django.shortcuts import render
from django.http import JsonResponse
from .models import DHTData, PumpData, SoilMoistureData, MotionData
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt

# Variable to simulate pump state
pump_state = False  # False means off, True means on


def get_latest_sensor_data(request):
    # Retrieve data from the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    dht_data = DHTData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    soil_data = SoilMoistureData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    motion_data = MotionData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    
    # Structure data for Chart.js
    response_data = {
        'temperature': [data.temperature for data in dht_data],
        'humidity': [data.humidity for data in dht_data],
        'soil_moisture': [data.moisture_level for data in soil_data],
        'motion': [1 if data.motion_detected else 0 for data in motion_data],
        'timestamps': [data.timestamp.strftime("%H:%M:%S") for data in dht_data]
    }
    return JsonResponse(response_data)

def dashboard(request):
   
    # one_hour_ago = timezone.now() - timedelta(hours=1)
    # pump_data = PumpData.objects.filter(timestamp__gte=one_hour_ago).order_by('timestamp')
    pump_data = PumpData.objects.last() 
    print("pumpdata", pump_data.pumpStatus) 
    pump_status = 'OFF'  # Default status
    if pump_data:
        print("in if loop")
        print("pumpdata", pump_data.pumpStatus)
        pump_status = pump_data.pumpStatus  # Assuming status stores 'ON' or 'OFF'
        return render(request, 'sensors/dashboard.html', {'pump_status': pump_status})

@csrf_exempt
def toggle_pump(request):

    global pump_state
    if request.method == "POST":
        # Toggle the pump state
        pump_state = not pump_state
        # Return the updated state as JSON
        return JsonResponse({"is_pump_on": pump_state})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

# Add the view for the pump control page
def pump_control(request):
    # Get the current state of the pump and pass it to the template
    is_pump_on = get_pump_status()  # Get the status of the pump
    return render(request, 'sensors/pump_control.html', {'is_pump_on': is_pump_on})

# A sample function to get the pump's current status (you can replace this with actual logic)
def get_pump_status():
    pump_data = PumpData.objects.last()
    pump_status = pump_data.pumpStatus if pump_data else 'OFF'
    return JsonResponse({'pump_status': pump_status})

def toggle_pump_logic():
    # This would contain the actual logic for turning the pump on/off
    # For simulation, we'll toggle the state and return it
    # For example, this could interact with an ESP32 to control the relay
    # You can change this logic as per your actual implementation
    return True  # Just returning True as a placeholder
