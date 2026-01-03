from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'exeats', views.ExeatViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'houses', views.HouseViewSet)

urlpatterns = [
    path('', views.exeat_list, name='exeat_list'),
    path('create/', views.exeat_create, name='exeat_create'),
    path('<int:pk>/', views.exeat_detail, name='exeat_detail'),
    path('<int:pk>/approve/', views.exeat_approve, name='exeat_approve'),
    path('add-student/', views.add_student, name='add_student'),
    path('add-house-mistress/', views.add_house_mistress, name='add_house_mistress'),
    path('add-house/', views.add_house, name='add_house'),
    path('security/', views.security_dashboard, name='security_dashboard'),
    path('security/sign-out/<int:pk>/', views.security_sign_out, name='security_sign_out'),
    path('security/sign-in/<int:pk>/', views.security_sign_in, name='security_sign_in'),
    path('api/', include(router.urls)),
]