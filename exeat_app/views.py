from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (Exeat, Student, HouseMistress, House, School, 
                     SubAdmin, SecurityPerson, CustomUser)
from .serializers import (
    ExeatSerializer, StudentSerializer, HouseMistressSerializer, HouseSerializer,
    ForgotPasswordSerializer, PasswordResetSerializer, SchoolSerializer,
    SubAdminSerializer, SecurityPersonSerializer,
    APIErrorResponseStructureSerializer, APISuccessResponseStructureSerializer
)

import random

User = get_user_model()


# ==================== PERMISSIONS ====================

class IsAdmin(permissions.BasePermission):
    """Only Django admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsSubAdmin(permissions.BasePermission):
    """Only Sub-Admin users"""
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'subadmin_profile')


class IsAdminOrSubAdmin(permissions.BasePermission):
    """Admin or Sub-Admin users"""
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or hasattr(request.user, 'subadmin_profile'))


# ==================== SCHOOL MANAGEMENT ====================

class SchoolViewSet(viewsets.ModelViewSet):
    """
    School management - Only accessible to Django admin users
    Allows creating and managing schools
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAdmin]


# ==================== SUB-ADMIN MANAGEMENT ====================

class SubAdminManagementViewSet(viewsets.ViewSet):
    """
    SubAdmin creation and management - Only for Django admin
    """
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['post'])
    def create_subadmin(self, request):
        """Create a new sub-admin for a school"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            school_id = request.data.get('school_id')
            phone = request.data.get('phone', '')

            # Validation
            if not all([username, email, password, school_id]):
                return Response(
                    {'error': 'username, email, password, and school_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check school exists
            school = get_object_or_404(School, id=school_id)

            # Check if school already has a sub-admin
            if SubAdmin.objects.filter(school=school).exists():
                return Response(
                    {'error': 'This school already has a sub-admin'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if username/email already exists
            CustomUser = get_user_model()
            if CustomUser.objects.filter(username=username).exists():
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if CustomUser.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user and sub-admin
            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role='subadmin',
                    school=school,
                    is_staff=False  # Sub-admin is not Django staff
                )

                sub_admin = SubAdmin.objects.create(
                    user=user,
                    school=school,
                    phone=phone
                )

            return Response(
                {
                    'message': 'Sub-admin created successfully',
                    'data': SubAdminSerializer(sub_admin).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== STUDENT MANAGEMENT ====================

class StudentManagementViewSet(viewsets.ModelViewSet):
    """
    Student management - Sub-admins can add students to their school
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrSubAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Student.objects.all()
        elif hasattr(user, 'subadmin_profile'):
            school = user.subadmin_profile.school
            return Student.objects.filter(school=school)
        return Student.objects.none()

    def create(self, request, *args, **kwargs):
        """Create a new student"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            student_id = request.data.get('student_id')
            name = request.data.get('name')
            phone = request.data.get('phone', '')
            house_id = request.data.get('house_id')
            guardian_name = request.data.get('guardian_name', '')
            guardian_phone = request.data.get('guardian_phone', '')

            if not all([username, email, password, student_id, name]):
                return Response(
                    {'error': 'username, email, password, student_id, and name are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determine school
            if request.user.is_staff:
                school_id = request.data.get('school_id')
                if not school_id:
                    return Response(
                        {'error': 'Admin must specify school_id'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                school = get_object_or_404(School, id=school_id)
            else:
                school = request.user.subadmin_profile.school

            # Check if student_id already exists in school
            if Student.objects.filter(school=school, student_id=student_id).exists():
                return Response(
                    {'error': 'Student ID already exists in this school'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if username/email exists
            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user and student
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.customuser.role = 'student'
                user.customuser.school = school
                user.customuser.save()

                house = None
                if house_id:
                    house = get_object_or_404(House, id=house_id, school=school)

                student = Student.objects.create(
                    user=user,
                    school=school,
                    student_id=student_id,
                    name=name,
                    email=email,
                    phone=phone,
                    house=house,
                    guardian_name=guardian_name,
                    guardian_phone=guardian_phone
                )

            return Response(
                {
                    'message': 'Student created successfully',
                    'data': StudentSerializer(student).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== HOUSE MISTRESS MANAGEMENT ====================

class HouseMistressManagementViewSet(viewsets.ModelViewSet):
    """
    House Mistress management - Sub-admins can add house mistresses to their school
    """
    serializer_class = HouseMistressSerializer
    permission_classes = [IsAdminOrSubAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return HouseMistress.objects.all()
        elif hasattr(user, 'subadmin_profile'):
            school = user.subadmin_profile.school
            return HouseMistress.objects.filter(school=school)
        return HouseMistress.objects.none()

    def create(self, request, *args, **kwargs):
        """Create a new house mistress"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            name = request.data.get('name')
            phone = request.data.get('phone', '')
            house_id = request.data.get('house_id')

            if not all([username, email, password, name, house_id]):
                return Response(
                    {'error': 'username, email, password, name, and house_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determine school
            if request.user.is_staff:
                school_id = request.data.get('school_id')
                if not school_id:
                    return Response(
                        {'error': 'Admin must specify school_id'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                school = get_object_or_404(School, id=school_id)
            else:
                school = request.user.subadmin_profile.school

            # Get house and verify it belongs to the school
            house = get_object_or_404(House, id=house_id, school=school)

            # Check if house already has a mistress
            if HouseMistress.objects.filter(house=house).exists():
                return Response(
                    {'error': 'This house already has a mistress'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if username/email exists
            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user and house mistress
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.customuser.role = 'house_mistress'
                user.customuser.school = school
                user.customuser.save()

                house_mistress = HouseMistress.objects.create(
                    user=user,
                    school=school,
                    name=name,
                    email=email,
                    phone=phone,
                    house=house
                )

            return Response(
                {
                    'message': 'House mistress created successfully',
                    'data': HouseMistressSerializer(house_mistress).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== SECURITY PERSONNEL MANAGEMENT ====================

class SecurityPersonManagementViewSet(viewsets.ModelViewSet):
    """
    Security Personnel management - Sub-admins can add security staff to their school
    """
    serializer_class = SecurityPersonSerializer
    permission_classes = [IsAdminOrSubAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SecurityPerson.objects.all()
        elif hasattr(user, 'subadmin_profile'):
            school = user.subadmin_profile.school
            return SecurityPerson.objects.filter(school=school)
        return SecurityPerson.objects.none()

    def create(self, request, *args, **kwargs):
        """Create a new security person"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            name = request.data.get('name')
            phone = request.data.get('phone', '')
            employee_id = request.data.get('employee_id', '')

            if not all([username, email, password, name]):
                return Response(
                    {'error': 'username, email, password, and name are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determine school
            if request.user.is_staff:
                school_id = request.data.get('school_id')
                if not school_id:
                    return Response(
                        {'error': 'Admin must specify school_id'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                school = get_object_or_404(School, id=school_id)
            else:
                school = request.user.subadmin_profile.school

            # Check if username/email exists
            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user and security person
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.customuser.role = 'security'
                user.customuser.school = school
                user.customuser.save()

                security_person = SecurityPerson.objects.create(
                    user=user,
                    school=school,
                    name=name,
                    email=email,
                    phone=phone,
                    employee_id=employee_id
                )

            return Response(
                {
                    'message': 'Security person created successfully',
                    'data': SecurityPersonSerializer(security_person).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== HOUSE MANAGEMENT ====================

class HouseManagementViewSet(viewsets.ModelViewSet):
    """
    House management - Sub-admins can create houses for their school
    """
    serializer_class = HouseSerializer
    permission_classes = [IsAdminOrSubAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return House.objects.all()
        elif hasattr(user, 'subadmin_profile'):
            school = user.subadmin_profile.school
            return House.objects.filter(school=school)
        return House.objects.none()

    def create(self, request, *args, **kwargs):
        """Create a new house"""
        try:
            name = request.data.get('name')
            description = request.data.get('description', '')

            if not name:
                return Response(
                    {'error': 'name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determine school
            if request.user.is_staff:
                school_id = request.data.get('school_id')
                if not school_id:
                    return Response(
                        {'error': 'Admin must specify school_id'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                school = get_object_or_404(School, id=school_id)
            else:
                school = request.user.subadmin_profile.school

            # Check if house name already exists in school
            if House.objects.filter(school=school, name=name).exists():
                return Response(
                    {'error': 'House already exists in this school'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            house = House.objects.create(
                school=school,
                name=name,
                description=description
            )

            return Response(
                {
                    'message': 'House created successfully',
                    'data': HouseSerializer(house).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== EXEAT MANAGEMENT ====================

class ExeatViewSet(viewsets.ModelViewSet):
    """
    Exeat management and approval
    """
    serializer_class = ExeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Exeat.objects.all()
        elif hasattr(user, 'subadmin_profile'):
            school = user.subadmin_profile.school
            return Exeat.objects.filter(school=school)
        elif hasattr(user, 'housemistress_profile'):
            house = user.housemistress_profile.house
            return Exeat.objects.filter(student__house=house)
        elif hasattr(user, 'security_profile'):
            school = user.security_profile.school
            return Exeat.objects.filter(school=school)
        else:
            return Exeat.objects.filter(student__user=user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an exeat"""
        exeat = self.get_object()
        user = request.user

        # Check authorization
        has_permission = (
            user.is_staff or
            (hasattr(user, 'subadmin_profile') and user.subadmin_profile.school == exeat.school) or
            (hasattr(user, 'housemistress_profile') and user.housemistress_profile.house.school == exeat.school)
        )

        if not has_permission:
            return Response(
                {'error': 'Not authorized to approve this exeat'},
                status=status.HTTP_403_FORBIDDEN
            )

        exeat.status = 'approved'
        exeat.approved_by = user
        exeat.save()

        return Response({
            'message': 'Exeat approved successfully',
            'data': ExeatSerializer(exeat).data
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an exeat"""
        exeat = self.get_object()
        user = request.user

        # Check authorization
        has_permission = (
            user.is_staff or
            (hasattr(user, 'subadmin_profile') and user.subadmin_profile.school == exeat.school) or
            (hasattr(user, 'housemistress_profile') and user.housemistress_profile.house.school == exeat.school)
        )

        if not has_permission:
            return Response(
                {'error': 'Not authorized to reject this exeat'},
                status=status.HTTP_403_FORBIDDEN
            )

        exeat.status = 'rejected'
        exeat.save()

        return Response({
            'message': 'Exeat rejected successfully',
            'data': ExeatSerializer(exeat).data
        })

    @action(detail=True, methods=['post'])
    def sign_out(self, request, pk=None):
        """Sign out a student (mark as left school)"""
        exeat = self.get_object()
        user = request.user

        # Only security can sign out
        if not (user.is_staff or hasattr(user, 'security_profile')):
            return Response(
                {'error': 'Only security personnel can sign out students'},
                status=status.HTTP_403_FORBIDDEN
            )

        if exeat.status != 'approved':
            return Response(
                {'error': 'Only approved exeats can be signed out'},
                status=status.HTTP_400_BAD_REQUEST
            )

        exeat.status = 'signed_out'
        exeat.signed_out_by = user
        exeat.signed_out_time = timezone.now()
        exeat.save()

        return Response({
            'message': 'Student signed out successfully',
            'data': ExeatSerializer(exeat).data
        })

    @action(detail=True, methods=['post'])
    def sign_in(self, request, pk=None):
        """Sign in a student (mark as returned)"""
        exeat = self.get_object()
        user = request.user

        # Only security can sign in
        if not (user.is_staff or hasattr(user, 'security_profile')):
            return Response(
                {'error': 'Only security personnel can sign in students'},
                status=status.HTTP_403_FORBIDDEN
            )

        if exeat.status != 'signed_out':
            return Response(
                {'error': 'Only signed out exeats can be signed in'},
                status=status.HTTP_400_BAD_REQUEST
            )

        exeat.status = 'signed_in'
        exeat.signed_in_by = user
        exeat.signed_in_time = timezone.now()
        exeat.save()

        return Response({
            'message': 'Student signed in successfully',
            'data': ExeatSerializer(exeat).data
        })


class AdminDashboardView(APIView):
    """
    Admin/SubAdmin dashboard showing exeat statistics
    """
    permission_classes = [IsAdminOrSubAdmin]

    def get(self, request):
        if request.user.is_staff:
            exeats = Exeat.objects.all()
            school_name = "All Schools"
        else:
            school = request.user.subadmin_profile.school
            exeats = Exeat.objects.filter(school=school)
            school_name = school.name

        total_exeats = exeats.count()
        approved_exeats = exeats.filter(status='approved').count()
        rejected_exeats = exeats.filter(status='rejected').count()
        pending_exeats = exeats.filter(status='pending').count()
        signed_out_exeats = exeats.filter(status='signed_out').count()
        signed_in_exeats = exeats.filter(status='signed_in').count()

        response_data = {
            "status": 200,
            "message": f"Dashboard data for {school_name}",
            "data": {
                "school": school_name,
                "total_exeats": total_exeats,
                "approved": approved_exeats,
                "rejected": rejected_exeats,
                "pending": pending_exeats,
                "signed_out": signed_out_exeats,
                "signed_in": signed_in_exeats,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
