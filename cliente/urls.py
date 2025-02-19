
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.Index.as_view()),
    path('login/',views.Login.as_view()),
    path('register/',views.Register.as_view()),
    path('verificacion/<str:email>/',views.Verificacion.as_view()),
    path('logout/',views.Logout.as_view()),
    path('forget_pass/',views.Forget_pass_email.as_view()),
    path('restore_pass/<str:tocken>/',views.Restore_pass.as_view()),
    path('set_2fa/',views.Set_2fa.as_view()),

    path('nueva_cita/<str:servicio>/',views.Agg_Cita.as_view()),
    path('mis_citas/',views.Mis_Citas.as_view()),
    path('cancelar_cita/',views.Cancelar_Cita.as_view()),

    path('set_antiphishing/',views.Set_antiphishing.as_view()),
    path('delete_antiphishing/',views.Delete_antiphishing.as_view()),
    path('perfil/',views.Perfil.as_view()),
    path('set_password/',views.Set_password.as_view()),

    path('nuevo_mensaje/',views.Nuevo_Mensaje.as_view()),
]