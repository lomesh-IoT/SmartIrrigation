from rest_framework.serializers import ModelSerializer
from .models import MotionData  # Import the model

class MotionDataSerializer(ModelSerializer):
    class Meta:
        model = MotionData
        fields = '__all__'  # or specify the fields you want to include
