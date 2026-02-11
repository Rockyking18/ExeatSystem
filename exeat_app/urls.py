from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# School Management
router.register(r'schools', views.SchoolViewSet, basename='school')

# Admin Management
router.register(r'subadmin', views.SubAdminManagementViewSet, basename='subadmin')

# User Management
router.register(r'students', views.StudentManagementViewSet, basename='student')
router.register(r'house-mistresses', views.HouseMistressManagementViewSet, basename='house-mistress')
router.register(r'security-personnel', views.SecurityPersonManagementViewSet, basename='security-person')
router.register(r'houses', views.HouseManagementViewSet, basename='house')

# Exeat Management
router.register(r'exeats', views.ExeatViewSet, basename='exeat')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]