from app1.user   import *
from django.urls import path

app_name = "userServices"

urlpatterns = [    
    #    user services
    path('userLogin/',             userLoginView,      name='userLoginView'),
    path('userRegister/',          userRegisterView,   name='userRegisterView'),
    path('forgetPass/',            forgetPass,         name='forgetPass'),
    path('changePass/',            changePass,         name='changePass'),
    path('resetPassword/',         resetPasswordView,  name='resetPasswordView'),
    path('userNemelt/',            userNemeltGet,      name='userNemeltMedeelelView'),
    path('verifyCode/',            verifyCodeView,     name='verifyCodeView'),
    path('userNemeltUp/',          userNemeltUpdate,   name='userNemeltUpdate'),
    path('verifyEmail/<str:otp>/', verifyEmailView,    name='verifyEmailView'),
    path('userNemeltIns/',         userNemeltInsert,   name='userNemeltInsert'),
    path('userInfoShow/',          userInfoShowView,   name='userInfoShow'),
    path('userInfoUpdate/',        userInfoUpdateView, name='uuserInfoUpdateView'),
    path('userEduUp/',             userEduUp,          name='userEduUp'),
    path('userFamily/',            userFamilyGet,      name= 'userFamilyGet'),
    path('userFamilyIns/',         userFamilyInsert,   name= 'userFamilyInsert'),
    path('userFamilyUp/',          userFamilyUpdate,   name= 'userFamilyUpdate'),
    ################################################################################
    path('userSocial/',            userSocial,         name='userSocial'),
    path('userSocialUp/',          userSocialUp,       name='userSocialup'),
    path('userSocialIn/',          userSocialIn,       name='userSocialIn'),
    ################################################################################
    path('userEduGet/',            userEduGet,         name='userEduGet'),
    path('userEduInsert/',         userEduInsert,      name='usereduInsert'),
    path('userTurshlaga/' ,        userTurshlaga,      name='userTurshlaga'   ),
    path('userTurshlagaUp/' ,      userTurshlagaUp,    name='userTurshlagaUp'   ),
    path('userTurshlagaIn/' ,      userTurshlagaIn,    name='userTurshlagaIn'   ),
    path('getUserSkill/' ,         getUserSkillView,   name='getUserSkillView'   ),
    path('setUserSkill/' ,         setUserSkillView,   name='setUserSkillView'   ),
    path('usedTemplateGet/' ,      usedTemplateGet,   name='usedTemplateGet'   ),
    path('uploadTemplate/' ,   uploadTemplateView,   name='uploadTemplateView'   ),
    path('getSkill/' ,         getSkillView,   name='getSkillView'   ),
    path('setSkill/' ,         setSkillView,   name='setSkillView'   ),
    ######################################################

    path('userList/',              userListView,       name='userListView'),
    ######################################################
    path('getTransactionLog/', getTransactionLog, name="getTransactionLog"),
    path('makeTransaction/', makeTransaction, name="makeTransaction"),
    ################################################################################
]
