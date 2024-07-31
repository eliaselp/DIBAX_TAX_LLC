from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
    path('forgot_pass/',views.forgot_pass_email.as_view()),
    path('verificacion/<str:email>/',views.forgot_pass_tocken.as_view()),
    path('restore_pass/<str:tocken>/',views.Restore_pass.as_view()),
    path('home/', views.Index.as_view()),
]
