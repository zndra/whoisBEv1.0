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
    path('verifyEmail/<str:otp>/', user.verifyEmailView,    name='verifyEmailView'),
    path('userNemeltIns/',         user.userNemeltInsert,   name='userNemeltInsert'),
    path('userInfoShow/',          user.userInfoShowView,   name='userInfoShow'),
    path('userInfoUpdate/',        user.userInfoUpdateView, name='uuserInfoUpdateView'),
    path('userEduUp/',             user.userEduUp,          name='userEduUp'),
    path('userFamily/',            user.userFamilyGet,      name= 'userFamilyGet'),
    ################################################################################
    path('userSocial/',            user.userSocial,         name='userSocial'),
    path('userSocialUp/',          user.userSocialUp,       name='userSocialup'),
    path('userSocialIn/',          user.userSocialIn,       name='userSocialIn'),
    ################################################################################
    path('userEduGet/',            user.userEduGet,         name='userEduGet'),
    path('userEduInsert/',         user.userEduInsert,      name='usereduInsert'),
    path('userTurshlaga/' ,        user.userTurshlaga,      name='userTurshlaga'   ),
    path('userTurshlagaUp/' ,      user.userTurshlagaUp,    name='userTurshlagaUp'   ),
    path('userTurshlagaIn/' ,      user.userTurshlagaIn,    name='userTurshlagaIn'   ),
    path('getUserSkill/' ,         user.getUserSkillView,   name='getUserSkillView'   ),
    path('setUserSkill/' ,         user.setUserSkillView,   name='setUserSkillView'   ),
    ######################################################

    # тестийн service-үүд. төслөө хverifyEmailийж дуусчаад устганаа.
    path('userList/',              user.userListView,       name='userListView'),
    path('zuu/',                   testViews.zuu,           name='zuuListView'),
    path('tavFact/',               testViews.tavFactView,   name='tavFactListView'),
    ######################################################
]
