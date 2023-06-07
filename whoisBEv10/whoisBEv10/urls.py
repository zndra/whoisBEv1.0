from django.urls import path
from app1 import basic

urlpatterns = [    
    path('zuu/', basic.zuu, name='zuu')
]
