from app1.user   import *
from app1.userTemps  import *
from django.urls import path
###############################################
from app1.profileFamilyViews   import *
from app1.userWork   import *
from app1.userEdu import *
from app1.userNemelt import *
from app1.userSocial import *
###############################################
from app1.tooAvahView import *
from app1.userTrans import *
from app1.userDash import *
from app1.userSkill import *

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
   path('verifyEmail/<str:otp>/', verifyEmailView, name='verifyEmailView'),
    path('userNemeltIns/',         userNemeltInsert,   name='userNemeltInsert'),
    path('userInfoShow/',          userInfoShowView,   name='userInfoShow'),
    path('userInfoUpdate/',        userInfoUpdateView, name='uuserInfoUpdateView'),
    path('getDashboardInfo/',      getDashboardInfoView,name='getDashboardInfoView'),
    path('insertComplain/',        insertComplainView, name='insertComplainView'),
    path('getComplain/',           getComplainView,    name='getComplainView'),
    ############# family ############################################################
    path('userFamily/',            userFamilyGet,      name= 'userFamilyGet'),
    path('userFamilyDel/',         userFamilyDel,      name= 'userFamilyDel'),
    path('userFamilyIns/',         userFamilyInsert,   name= 'userFamilyInsert'),
    path('userFamilyUp/',          userFamilyUpdate,   name= 'userFamilyUpdate'),
    ############## social ##################################################################
    path('userSocial/',            userSocial,         name='userSocial'),
    path('userSocialUp/',          userSocialUp,       name='userSocialup'),
    path('userSocialIn/',          userSocialIn,       name='userSocialIn'),
    path('userSocialDel/',         userSocialDel,      name='userSocialDel'),
    ############### education ################################################################
    path('userEduGet/',            userEduGet,         name='userEduGet'),
    path('userEduUp/',             userEduUp,          name='userEduUp'),
    path('userEduInsert/',         userEduInsert,      name='usereduInsert'),
    path('userEduDel/',            userEduDel,         name='userEduDel'),
    ########################################################################################
    path('userTurshlaga/' ,        userTurshlaga,      name='userTurshlaga'   ),
    path('userTurshlagaUp/' ,      userTurshlagaUp,    name='userTurshlagaUp'   ),
    path('userTurshlagaIn/' ,      userTurshlagaIn,    name='userTurshlagaIn'   ),
    path('userTurshlagaDel/' ,      userTurshlagaDel,    name='userTurshlagaDel'   ),
    path('getUserSkill/' ,         getUserSkillView,   name='getUserSkillView'   ),
    path('setUserSkill/' ,         setUserSkillView,   name='setUserSkillView'   ),
    #######################################################
    path('userTempGet/' ,         userTempGet,   name='userTempGet'   ),
    path('tempGet/' ,         tempGet,   name='tempGet'   ),
    path('userTemplates/' ,     userTemplates,   name='usedTemplates'   ),
    path('uploadTemplate/' ,   uploadTemplateView,   name='uploadTemplateView'   ),
    path('tempList/' ,   tempListView,   name='tempListView'   ),
    path('userTempList/' ,   userTempListView,   name='userTempListView'   ),
    path('userAllInfo/' ,   getUserAllInfo,   name='getUserAllInfo'   ),
    path('userTempDel/' ,   userTempDel,   name='userTempDel'   ),
    path('tempDel/' ,   tempDel,   name='tempDel'   ),
    ##########################################################################
    path('getSkill/' ,         getSkillView,   name='getSkillView'   ),
    path('insertUserSkill/' ,         insertUserSkillView,   name='insertUserSkillView'   ),
    path('delUserSkill/' ,         delUserSkillView,   name='delUserSkillView'   ),
    path('setSkill/' ,         setSkillView,   name='setSkillView'   ),
    path('userList/',              userListView,       name='userListView'),
    path('userList/',              userListView,       name='userListView'),
    path('fLog/',              fLog,       name='fLogView'),
    ######################################################
    path('getTransactionLog/', getTransactionLog, name="getTransactionLog"),
    path('makeTransaction/', makeTransactionView, name="makeTransaction"),
    path('adminTrans/', adminTransactionView, name="adminTransactionView"),
    path('getAdminLog/', getAdminTransactionLog, name="getAdminTransactionLog"),

    ################################################################################
     path('tooAvah/', tooAvah, name="tooAvah"),
]
