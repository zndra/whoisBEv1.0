from django.urls import path
from app1 import user
urlpatterns = [    
    #    user servoces
    path('userList/', user.userListView, name='userListView'),
    ######################################################
]
