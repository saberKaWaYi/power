from django.urls import path
from .views import get_data

urlpatterns = [
    path('get_data', get_data, name='get_data'),
]