from app1        import user, testViews
from django.urls import path
urlpatterns = [    
    #    user servoces
    path('userLogin/',             user.userLoginView,      name='userLoginView'),
    path('userRegister/',          user.userRegisterView,   name='userRegisterView'),
    path('forgetPass/',            user.forgetPass,         name='forgetPass'),
    path('changePass/',            user.changePass,         name='changePass'),
    path('resetPassword/',         user.resetPasswordView,  name='resetPasswordView'),
    path('userNemelt/',            user.userNemeltGet,      name='userNemeltMedeelelView'),
    path('verifyCode/',            user.verifyCodeView,     name='verifyCodeView'),
    path('userNemeltUp/',          user.userNemeltUpdate,   name='userNemeltUpdate'),
    path('updateUser/',            user.updateUserView,     name='updateUserView'),
    path('verifyEmail/<str:otp>/', user.verifyEmailView,    name='verifyEmailView'),
    path('userNemeltIns/',         user.userNemeltInsert,   name='userNemeltInsert'),
    path('userEdu/',               user.userEdu,            name='userEdu'),
    path('userSocial/',            user.userSocial,         name='userSocial'),
    ######################################################

    # тестийн service-үүд. төслөө хverifyEmailийж дуусчаад устганаа.
    path('userList/',              user.userListView,       name='userListView'),
    path('zuu/',                   testViews.zuu,           name='zuuListView'),
    path('tavFact/',               testViews.tavFactView,   name='tavFactListView'),
    ######################################################
]
