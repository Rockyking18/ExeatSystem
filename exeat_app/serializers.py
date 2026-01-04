from rest_framework import serializers
from .models import Student, Exeat, HouseMistress, House

class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    house = HouseSerializer(read_only=True)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Student
        fields = '__all__'

class HouseMistressSerializer(serializers.ModelSerializer):
    house = HouseSerializer(read_only=True)

    class Meta:
        model = HouseMistress
        fields = '__all__'

class ExeatSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    signed_out_by = serializers.StringRelatedField(read_only=True)
    signed_in_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Exeat
        fields = '__all__'

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)


class APISuccessResponseStructureSerializer(serializers.Serializer):
    """Standard structure for API success responses"""
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.JSONField()

class APIErrorResponseStructureSerializer(serializers.Serializer):
    """Standard structure for API error responses"""
    status = serializers.IntegerField()
    message = serializers.CharField()
    errors = serializers.JSONField()