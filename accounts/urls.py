from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('login', views.login,name='login'),
    path('logout', views.logout,name='logout'),
    # path('api-auth/', include('rest_framework.urls')),
    path('ap/', views.registerView.as_view(),name="ap"),
    path('ap/login', views.LoginView.as_view(),name="login"), 
    path('ap/logout', views.LogoutView.as_view(),name="logout"), 
    path('activate/<uidb64>/<token>', views.activate,name='activate')
]

