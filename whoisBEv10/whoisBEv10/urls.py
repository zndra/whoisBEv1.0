from django.urls import path
from app1 import basic,user

urlpatterns = [    
    #    bagic servoces
    path('zuu/', basic.zuu, name='zuu'),# test
    ######################################################

    #    user servoces
    path('userList/', user.userListView, name='userListView'),
    ######################################################
]
