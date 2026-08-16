from django.urls import path

from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:pk>/complete/', views.mark_completed, name='mark_completed'),
]
