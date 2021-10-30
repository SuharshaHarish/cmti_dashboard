from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.redirect_to_home, name='redirect_to_home'),
    path('home/', views.home, name='home'),
    path('anomaly/', views.anomaly_view, name='anomaly'),
    path('graphs/', views.graphs, name='graphs'),
]

