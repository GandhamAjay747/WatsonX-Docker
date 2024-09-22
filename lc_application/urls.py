from django.urls import path
from . import views

urlpatterns = [
    path('registrationForm/', views.registrationForm, name='registrationForm'),
    path('loginForm/', views.loginForm, name='loginForm'),
    path('dashboardPage/', views.dashboardPage, name='dashboardPage'),
    path('add_lc/', views.add_lc, name='add_lc'),   
    path('view_lc/', views.view_lc, name='view_lc'),
    path('approve_lc/<int:lc_id>/', views.approve_lc, name='lc_approve'),
    path('predict_lc/', views.predict_lc, name='lc_predict'),
   #path('', views.add_lc, name='welcomepage'),
    path('edit_lc/<int:lc_id>/', views.edit_lc, name='edit_lc'),
    path('delete_lc/<int:lc_id>/', views.delete_lc, name='delete_lc'),
    path('navbar/', views.navbar, name='navbar'),
    path('sidebar/', views.sidebar, name='sidebar'),
    
]
