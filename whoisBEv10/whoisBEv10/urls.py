from django.urls import path
from app1 import user, basic

urlpatterns = [    
    #    user servoces
    path('userList/', user.userListView, name='userListView'),
    path('userLogin/', user.userLoginView, name='userLoginView'),
    path('zuu/', basic.zuu, name='zuuListView'),
    path('userRegister/', user.userRegisterView, name='userRegisterView'),
    ######################################################
]
