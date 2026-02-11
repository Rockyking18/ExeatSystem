from time import timezone
from django.db import models
from django.contrib.auth.models import  AbstractUser, User
from exeat.settings import AUTH_USER_MODEL
AUTH_USER_MODEL


class School(models.Model):
    """School/Institution model"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class SubAdmin(models.Model):
    """School Sub-Admin model"""
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subadmin_profile')
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='sub_admin')
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.school.name}"

    class Meta:
        verbose_name = "Sub Admin"
        verbose_name_plural = "Sub Admins"


class House(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='houses')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('school', 'name')
        ordering = ['school', 'name']

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Student(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    student_id = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('school', 'student_id')
        ordering = ['school', 'name']

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class HouseMistress(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='housemistress_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='house_mistresses')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    house = models.OneToOneField(House, on_delete=models.CASCADE, related_name='house_mistress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "House Mistress"
        verbose_name_plural = "House Mistresses"
        ordering = ['school', 'name']

    def __str__(self):
        return f"{self.name} - {self.house.name} ({self.school.name})"


class SecurityPerson(models.Model):
    """Security personnel model"""
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='security_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='security_personnel')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Security Person"
        verbose_name_plural = "Security Personnel"
        ordering = ['school', 'name']

    def __str__(self):
        return f"{self.name} - {self.school.name}"




class Exeat(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('signed_out', 'Signed Out'),
        ('signed_in', 'Signed In'),
        ('overdue', 'Overdue'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exeats', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exeats')
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

    class Meta:
        ordering = ['-created_at']

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
        ('house_mistress', 'House Mistress'),
        ('security', 'Security'),
        ('subadmin', 'Sub Admin'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def set_otp(self, code):
        self.otp = code
        self.otp_created_at = timezone.now()
        self.save()
    
    def is_otp_valid(self):
        if self.otp_created_at:
            # OTP valid for 5 minutes (adjust as needed)
            return (timezone.now() - self.otp_created_at) < timezone.timedelta(minutes=5)
        return False