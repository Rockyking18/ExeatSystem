from django.db import models
from django.contrib.auth.models import  AbstractUser, User
from exeat.settings import AUTH_USER_MODEL
AUTH_USER_MODEL
class House(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    def __str__(self):
        return self.name

class HouseMistress(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    house = models.OneToOneField(House, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.house}"

class Exeat(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('signed_out', 'Signed Out'),
        ('signed_in', 'Signed In'),
        ('overdue', 'Overdue'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_exeats')
    signed_out_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_out_exeats')
    signed_out_time = models.DateTimeField(null=True, blank=True)
    signed_in_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_in_exeats')
    signed_in_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Exeat for {self.student.name} - {self.status}"

    def is_overdue(self):
        from django.utils import timezone
        if self.status == 'signed_out' and timezone.now() > self.end_date:
            return True
        return False
    

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('subadmin', 'Sub Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
