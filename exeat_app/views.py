from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Exeat, Student, HouseMistress, House
from .serializers import ExeatSerializer, StudentSerializer, HouseMistressSerializer, HouseSerializer

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

@login_required
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
    if not request.user.is_staff:
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