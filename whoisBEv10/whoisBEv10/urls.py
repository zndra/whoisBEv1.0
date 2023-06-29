from app1        import user, testViews
from django.urls import path, include
urlpatterns = [    
    #    user services
    path("", include("app1.routes.userUrls", namespace='userServices')),

    # тестийн service-үүд. төслөө хverifyEmailийж дуусчаад устганаа.
    path('zuu/',                   testViews.zuu,           name='zuuListView'),
    path('tavFact/',               testViews.tavFactView,   name='tavFactListView'),
    ################################################################################
]