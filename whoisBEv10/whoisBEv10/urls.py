from app1        import user, basic
from django.urls import path
urlpatterns = [    
    #    user servoces
    path('userList/',           user.userListView,       name='userListView'),
    path('userLogin/',          user.userLoginView,      name='userLoginView'),
    path('zuu/',                basic.zuu,               name='zuuListView'),
    path('userRegister/',       user.userRegisterView,   name='userRegisterView'),
    path('forgetPass/',         user.forgetPass,         name='forgetPass'),
    path('changePass/',         user.changePass,         name='changePass'),
    path('userNemeltMedeelel/', user.userNemeltMedeelel, name='userNemeltMedeelelView'),
    ######################################################
]
