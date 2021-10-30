"""opcua_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
# from opcua_app.opcua_client import start_client
# from background_task.models import Task
from datetime import datetime,timedelta

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('opcua_app.urls'))
]

# current_time = datetime.now()
# # current_time = datetime(year=2021,month=10,day=26,hour=17)
# if current_time.hour < 9:
#     start = datetime(year=current_time.year,month=current_time.month,day=current_time.day,hour=9)
# elif current_time.hour >= 17:
#     next_day = datetime(year=current_time.year,month=current_time.month,day=current_time.day) + timedelta(days=1)
#     start = datetime(year=next_day.year,month=next_day.month,day=next_day.day,hour=9)
# start_client(repeat=Task.DAILY)