from linecache import cache
from urllib import request
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status, views
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Exeat, Student, HouseMistress, House
from .serializers import APIErrorResponseStructureSerializer, APISuccessResponseStructureSerializer, ExeatSerializer, StudentSerializer, HouseMistressSerializer, HouseSerializer, ForgotPasswordSerializer, PasswordResetSerializer    
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
import random
from django.shortcuts import render, redirect
from .models import CustomUser
from exeat.settings import AUTH_USER_MODEL
AUTH_USER_MODEL



class ExeatForm(forms.ModelForm):
    class Meta:
        model = Exeat
        fields = ['reason', 'start_date', 'end_date']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'email', 'phone', 'house', 'guardian_name', 'guardian_phone', 'photo']

class HouseMistressForm(forms.ModelForm):
    class Meta:
        model = HouseMistress
        fields = ['name', 'email', 'phone', 'house']

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['name', 'description']



class LoginView(request):
    def post(self, request):
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_superuser or user.is_staff:
                    return redirect('admin')
                elif hasattr(user, 'role') and user.role == 'staff':
                    return redirect('staff-dashboard')
                elif hasattr(user, 'role') and user.role == 'student':
                    return redirect('student-dashboard')
                elif hasattr(user, 'role') and user.role == 'subadmin':
                    return redirect('subadmin-dashboard')
            else:
                return render(request, 'auth/login.html', {'error': 'Invalid credentials'})
        return render(request, 'auth/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')

    



class ForgotPasswordView(request):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp

            send_mail(
                'Your Password Reset OTP',
                f'Use this OTP to reset your password: {otp}',
                'noreply@example.com',
                [email],
                fail_silently=False,
            )
            return redirect('verify_otp') 
        except User.DoesNotExist:
            return Response(
                APIErrorResponseStructureSerializer({
                    "status": 400,
                    "message": "Email not found",
                    "errors": ["No user is associated with this email address."]
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(request):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            entered_otp = request.POST['otp']
        session_otp = request.session.get('reset_otp')
        email = request.session.get('reset_email')

        if entered_otp == session_otp and email:
            if not session_otp:
                error_data = {
                "status": 400,
                "message": "OTP expired or not found",
                "errors": ["Your reset code has expired. Please request a new one."]
                }
            return Response(
                APIErrorResponseStructureSerializer(error_data).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        if entered_otp != session_otp:
            error_data = {
                "status": 400,
                "message": "Invalid OTP",
                "errors": ["The reset code you entered is incorrect. Please check and try again."]
            }
            return Response(
                APIErrorResponseStructureSerializer(error_data).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        cache.delete(f"reset_otp_{User.email}")

        response_data = {
                "status": 200,
                "message": "Password successfully reset",
                "data": {
                    "message": "You can now login with your new password"
                }
            }
        return Response(
                APISuccessResponseStructureSerializer(response_data).data,
                status=status.HTTP_200_OK
            )

    error_data = {
        "status": 400,
        "message": "Password reset failed",
        "errors": ""
    }


@login_required
def exeat_list(request):
    user = request.user
    if user.is_staff:
        exeats = Exeat.objects.all()
        total_exeats = exeats.count()
        approved_exeats = exeats.filter(status='approved').count()
        rejected_exeats = exeats.filter(status='rejected').count()
        pending_exeats = exeats.filter(status='pending').count()
        context = {
            'exeats': exeats,
            'total_exeats': total_exeats,
            'approved_exeats': approved_exeats,
            'rejected_exeats': rejected_exeats,
            'pending_exeats': pending_exeats,
        }
    elif HouseMistress.objects.filter(user=user).exists():
        house_mistress = HouseMistress.objects.get(user=user)
        exeats = Exeat.objects.filter(student__house=house_mistress.house)
        context = {'exeats': exeats, 'is_house_mistress': True}
    else:
        student = get_object_or_404(Student, user=user)
        exeats = Exeat.objects.filter(student=student)
        context = {'exeats': exeats}
    return render(request, 'exeat_app/exeat_list.html', context)

@login_required
def exeat_create(request):
    if request.method == 'POST':
        form = ExeatForm(request.POST)
        if form.is_valid():
            exeat = form.save(commit=False)
            exeat.student = get_object_or_404(Student, user=request.user)
            exeat.save()
            return redirect('exeat_list')
    else:
        form = ExeatForm()
    return render(request, 'exeat_app/exeat_form.html', {'form': form})

@login_required
def exeat_detail(request, pk):
    exeat = get_object_or_404(Exeat, pk=pk)
    return render(request, 'exeat_app/exeat_detail.html', {'exeat': exeat})

@login_required
def exeat_approve(request, pk):
    user = request.user
    exeat = get_object_or_404(Exeat, pk=pk)
    if user.is_staff or (HouseMistress.objects.filter(user=user, house=exeat.student.house).exists()):
        exeat.status = 'approved'
        exeat.approved_by = user
        exeat.save()
    return redirect('exeat_list')


@login_required
class AdminAddViews:
    def add_student(request):
        if not request.user.is_staff:
            return redirect('exeat_list')
        if request.method == 'POST':
            form = StudentForm(request.POST)
            if form.is_valid():
                student = form.save(commit=False)
                # Create user
                username = student.student_id  # Use student_id as username
                password = User.objects.make_random_password()
                user = User.objects.create_user(username=username, email=student.email, password=password)
                student.user = user
                student.save()
                # Send email
                from django.core.mail import send_mail
                send_mail(
                    'Your Account Details',
                    f'Username: {username}\nPassword: {password}',
                    'admin@example.com',
                    [student.email],
                    fail_silently=False,
                )
                return redirect('exeat_list')
        else:
            form = StudentForm()
        return render(request, 'exeat_app/add_student.html', {'form': form})

    def add_house_mistress(request):
        if not request.user.is_staff:
            return redirect('exeat_list')
        if request.method == 'POST':
            form = HouseMistressForm(request.POST)
            if form.is_valid():
                house_mistress = form.save(commit=False)
                # Create user
                username = house_mistress.name.lower().replace(' ', '_')  # Simple username
                password = User.objects.make_random_password()
                user = User.objects.create_user(username=username, email=house_mistress.email, password=password)
                house_mistress.user = user
                house_mistress.save()
                # Send email
                from django.core.mail import send_mail
                send_mail(
                    'Your Account Details',
                    f'Username: {username}\nPassword: {password}',
                    'admin@example.com',
                    [house_mistress.email],
                    fail_silently=False,
                )
                return redirect('exeat_list')
        else:
            form = HouseMistressForm()
        return render(request, 'exeat_app/add_house_mistress.html', {'form': form})

@login_required
def security_sign_out(request, pk):
    if not request.user.groups.filter(name='Security').exists() and not request.user.is_staff:
        return redirect('exeat_list')
    exeat = get_object_or_404(Exeat, pk=pk, status='approved')
    if request.method == 'POST':
        exeat.status = 'signed_out'
        exeat.signed_out_by = request.user
        exeat.signed_out_time = timezone.now()
        exeat.save()
        return redirect('security_dashboard')
    return render(request, 'exeat_app/security_sign_out.html', {'exeat': exeat})

@login_required
def security_sign_in(request, pk):
    if not request.user.groups.filter(name='Security').exists() and not request.user.is_staff:
        return redirect('exeat_list')
    exeat = get_object_or_404(Exeat, pk=pk, status='signed_out')
    if request.method == 'POST':
        exeat.status = 'signed_in'
        exeat.signed_in_by = request.user
        exeat.signed_in_time = timezone.now()
        exeat.save()
        return redirect('security_dashboard')
    return render(request, 'exeat_app/security_sign_in.html', {'exeat': exeat})

@login_required
def security_dashboard(request):
    if not request.user.groups.filter(name='Security').exists() and not request.user.is_staff:
        return redirect('exeat_list')
    exeats = Exeat.objects.filter(status__in=['approved', 'signed_out'])
    return render(request, 'exeat_app/security_dashboard.html', {'exeats': exeats})

# API Views
class ExeatViewSet(viewsets.ModelViewSet):
    queryset = Exeat.objects.all()
    serializer_class = ExeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Exeat.objects.all()
        elif HouseMistress.objects.filter(user=user).exists():
            house_mistress = HouseMistress.objects.get(user=user)
            return Exeat.objects.filter(student__house=house_mistress.house)
        else:
            student = get_object_or_404(Student, user=user)
            return Exeat.objects.filter(student=student)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = request.user
        exeat = self.get_object()
        if user.is_staff or (HouseMistress.objects.filter(user=user, house=exeat.student.house).exists()):
            exeat.status = 'approved'
            exeat.approved_by = user
            exeat.save()
            return Response({'status': 'approved'})
        return Response({'error': 'Not authorized'}, status=403)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Student.objects.all()
        return Student.objects.filter(user=self.request.user)

@login_required
def add_house(request):
    if not request.user.is_subadmin:
        return redirect('exeat_list')
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exeat_list')
    else:
        form = HouseForm()
    return render(request, 'exeat_app/add_house.html', {'form': form})

# API Views
class ExeatViewSet(viewsets.ModelViewSet):
    queryset = Exeat.objects.all()
    serializer_class = ExeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Exeat.objects.all()
        elif HouseMistress.objects.filter(user=user).exists():
            house_mistress = HouseMistress.objects.get(user=user)
            return Exeat.objects.filter(student__house=house_mistress.house)
        else:
            student = get_object_or_404(Student, user=user)
            return Exeat.objects.filter(student=student)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = request.user
        exeat = self.get_object()
        if user.is_staff or (HouseMistress.objects.filter(user=user, house=exeat.student.house).exists()):
            exeat.status = 'approved'
            exeat.approved_by = user
            exeat.save()
            return Response({'status': 'approved'})
        return Response({'error': 'Not authorized'}, status=403)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Student.objects.all()
        return Student.objects.filter(user=self.request.user)

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [permissions.IsAuthenticated]


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({'status': 'logged in'})
        return Response({'error': 'Invalid credentials'}, status=400)
    


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'status': 'logged out'})
    
class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def reset(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            from django.core.mail import send_mail
            send_mail(
                'Password Reset',
                f'Your new password is: {new_password}',
                '<EMAIL>',
                [email],    
                fail_silently=False,
            )       
            return Response({'status': 'Password reset. Check your email.'})
        except User.DoesNotExist:
            return Response({'error': 'Email not found'}, status=400)
        return Response(
                APISuccessResponseStructureSerializer(response_data).data,  
                status=status.HTTP_200_OK
            )
    
@login_required
class AdmintDashboardView(APIView):
    """
    Admin dashboard showing all complaints across all categories.
    Admins have full access to view and manage all complaints.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "admin":
            error_data = {
                "status": 403,
                "message": "Unauthorized. Admin access required.",
                "errors": ["You must be an admin to access this resource"]
            }
            return Response(
                APIErrorResponseStructureSerializer(error_data).data,
                status=status.HTTP_403_FORBIDDEN
            )

        Exeat = Exeat.objects.all()

        # Filter by status
        status_param = request.query_params.get("status")
        if status_param:
            Exeat = Exeat.filter(status=status_param)

        # Filter by category
        category_param = request.query_params.get("category")
        if category_param:
            Exeat = Exeat.filter(category=category_param)

        # Filter by date range
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")
        if start_date and end_date:
            Exeat = Exeat.filter(created_at__date__range=[start_date, end_date])    

        Exeat = Exeat.order_by('-created_at')
        serializer = ExeatSerializer(Exeat, many=True)

        response_data = {
            "status": 200,
            "message": "All complaints retrieved successfully",
            "data": {
                "total": Exeat.count(),
                "complaints": serializer.data
            }
        }

        return Response(
            APISuccessResponseStructureSerializer(response_data).data,
            status=status.HTTP_200_OK
        )
    
