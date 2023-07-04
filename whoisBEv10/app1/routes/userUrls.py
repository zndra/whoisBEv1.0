from app1.user   import *
from app1.userTemps  import *
from django.urls import path

###############################################
from app1.profileFamilyViews   import *
from app1.userWork   import *
from app1.userEdu import *
###############################################
from app1.tooAvahView import *

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
    ############# family ############################################################
    path('userFamily/',            userFamilyGet,      name= 'userFamilyGet'),
    path('userFamilyDel/',         userFamilyDel,      name= 'userFamilyDel'),
    path('userFamilyIns/',         userFamilyInsert,   name= 'userFamilyInsert'),
    path('userFamilyUp/',          userFamilyUpdate,   name= 'userFamilyUpdate'),
    ################################################################################
    path('userSocial/',            userSocial,         name='userSocial'),
    path('userSocialUp/',          userSocialUp,       name='userSocialup'),
    path('userSocialIn/',          userSocialIn,       name='userSocialIn'),
    path('userSocialDel/',         userSocialDel,      name='userSocialDel'),
    ################################################################################
    path('userEduGet/',            userEduGet,         name='userEduGet'),
    path('userEduInsert/',         userEduInsert,      name='usereduInsert'),
    path('userEduDel/',            userEduDel,         name='userEduDel'),
    path('userTurshlaga/' ,        userTurshlaga,      name='userTurshlaga'   ),
    path('userTurshlagaUp/' ,      userTurshlagaUp,    name='userTurshlagaUp'   ),
    path('userTurshlagaIn/' ,      userTurshlagaIn,    name='userTurshlagaIn'   ),
    path('userTurshlagaDel/' ,      userTurshlagaDel,    name='userTurshlagaDel'   ),
    path('getUserSkill/' ,         getUserSkillView,   name='getUserSkillView'   ),
    path('setUserSkill/' ,         setUserSkillView,   name='setUserSkillView'   ),
    path('userTempGet/' ,         userTempGet,   name='userTempGet'   ),
    path('tempGet/' ,         tempGet,   name='tempGet'   ),
    path('userTemplates/' ,     userTemplates,   name='usedTemplates'   ),
    path('uploadTemplate/' ,   uploadTemplateView,   name='uploadTemplateView'   ),
    path('tempList/' ,   tempListView,   name='tempListView'   ),
    path('userTempList/' ,   userTempListView,   name='userTempListView'   ),
    path('userAllInfo/' ,   getUserAllInfo,   name='getUserAllInfo'   ),
    path('getSkill/' ,         getSkillView,   name='getSkillView'   ),
    path('setSkill/' ,         setSkillView,   name='setSkillView'   ),
    


    path('userList/',              userListView,       name='userListView'),
    ######################################################
    path('getTransactionLog/', getTransactionLog, name="getTransactionLog"),
    path('makeTransaction/', makeTransactionView, name="makeTransaction"),
    ################################################################################
     path('tooAvah/', tooAvah, name="tooAvah"),
]
