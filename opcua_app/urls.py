from django.urls import path,include
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('anomaly/', views.anomaly_view, name='anomaly'),
    path('graphs/', views.graphs, name='graphs'),
]

