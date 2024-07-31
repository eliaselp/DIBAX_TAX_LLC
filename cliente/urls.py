
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.Index.as_view()),
    path('login/',views.Login.as_view()),
    path('register/',views.Register.as_view()),
    path('verificacion/<str:email>/',views.Verificacion.as_view()),
    path('logout/',views.Logout.as_view()),
    path('forget_pass/',views.Forget_pass_email.as_view()),
    path('restore_pass/<str:tocken>/',views.Restore_pass.as_view())
]
