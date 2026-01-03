from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'exeats', views.ExeatViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'houses', views.HouseViewSet)
router.register(r'login', views.LoginViewSet, basename='login')
router.register(r'logout', views.LogoutViewSet, basename='logout')
router.register(r'PasswordReset', views.PasswordResetViewSet, basename='password_reset')


#Authentication URLs
auth_urls = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', views.PasswordResetView, name='password_reset'),
]

# Admin URLs
admin_urls = [
    path('add-student/', views.add_student, name='add_student'),
    path('add-house-mistress/', views.add_house_mistress, name='add_house_mistress'),
    path('add-house/', views.add_house, name='add_house'),
    path('<int:pk>/approve/', views.exeat_approve, name='exeat_approve'),
]

# Student URLs
student_urls = [
    path('', views.exeat_list, name='exeat_list'),
    path('create/', views.exeat_create, name='exeat_create'),
    path('<int:pk>/', views.exeat_detail, name='exeat_detail'),
]

# Staff URLs (House Mistresses)
staff_urls = [
    # Add staff-specific URLs here if any
]

# Security URLs
security_urls = [
    path('security/', views.security_dashboard, name='security_dashboard'),
    path('security/sign-out/<int:pk>/', views.security_sign_out, name='security_sign_out'),
    path('security/sign-in/<int:pk>/', views.security_sign_in, name='security_sign_in'),
]

# API URLs
api_urls = [
    path('api/', include(router.urls)),
]

urlpatterns = admin_urls + student_urls + staff_urls + security_urls + api_urls