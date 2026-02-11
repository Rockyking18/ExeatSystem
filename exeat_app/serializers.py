from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Student, Exeat, HouseMistress, House, School, SubAdmin, SecurityPerson

User = get_user_model()


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'email', 'phone', 'address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class HouseSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        write_only=True,
        source='school'
    )

    class Meta:
        model = House
        fields = ['id', 'school', 'school_id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    house = HouseSerializer(read_only=True)
    house_id = serializers.PrimaryKeyRelatedField(
        queryset=House.objects.all(),
        write_only=True,
        required=False,
        source='house'
    )
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        write_only=True,
        source='school'
    )
    photo = serializers.ImageField(required=False)
    username = serializers.CharField(source='user.username', read_only=True)
    email_user = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'school', 'school_id', 'student_id', 'name', 'email', 'username', 
                  'email_user', 'phone', 'house', 'house_id', 'guardian_name', 'guardian_phone', 
                  'photo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class HouseMistressSerializer(serializers.ModelSerializer):
    house = HouseSerializer(read_only=True)
    house_id = serializers.PrimaryKeyRelatedField(
        queryset=House.objects.all(),
        write_only=True,
        source='house'
    )
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        write_only=True,
        source='school'
    )
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = HouseMistress
        fields = ['id', 'user', 'school', 'school_id', 'name', 'email', 'username', 'phone', 
                  'house', 'house_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SecurityPersonSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        write_only=True,
        source='school'
    )
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SecurityPerson
        fields = ['id', 'user', 'school', 'school_id', 'name', 'email', 'username', 'phone', 
                  'employee_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SubAdminSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        write_only=True,
        source='school'
    )
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = SubAdmin
        fields = ['id', 'user', 'school', 'school_id', 'username', 'email', 'first_name', 
                  'last_name', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ExeatSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        write_only=True,
        source='student'
    )
    school = SchoolSerializer(read_only=True)
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        write_only=True,
        source='school'
    )
    approved_by = serializers.StringRelatedField(read_only=True)
    signed_out_by = serializers.StringRelatedField(read_only=True)
    signed_in_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Exeat
        fields = ['id', 'school', 'school_id', 'student', 'student_id', 'reason', 'start_date', 
                  'end_date', 'status', 'approved_by', 'signed_out_by', 'signed_out_time', 
                  'signed_in_by', 'signed_in_time', 'created_at', 'updated_at']
        read_only_fields = ['id', 'approved_by', 'signed_out_by', 'signed_in_by', 'created_at', 'updated_at']

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