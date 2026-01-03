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