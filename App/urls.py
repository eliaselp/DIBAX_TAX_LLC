from django.urls import path
from . import views
urlpatterns = [
    path('',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
    path('forgot_pass/',views.forgot_pass_email.as_view()),
    path('verificacion/<str:email>/',views.forgot_pass_tocken.as_view()),
    path('restore_pass/<str:tocken>/',views.Restore_pass.as_view()),
    path('home/', views.Index.as_view()),
    
    path('set_meta/<str:tipo>/',views.set_Meta.as_view()),
    path('remove_meta/<str:tipo>/',views.Remove_meta.as_view()),
    path('estado_servicio/',views.Estado_Servicio.as_view()),

    path('bloquear_fechas/',views.Bloquear_Fecha.as_view()),
    path('habilitar_fechas/',views.Habilitar_Fecha.as_view()),

    path('citas_aprobadas/',views.Citas_Aprobadas.as_view()),
    path('citas_pendientes/',views.Citas_Pendientes.as_view()),
    path('nueva_cita/<str:servicio>/',views.Agg_Cita.as_view()),
    path('denegar_cita/<int:cita>/',views.Denegar_Cita.as_view()),
    path('editar_cita/<str:servicio>/',views.Editar_Cita.as_view()),
    path('aprobar_cita/',views.Aprobar_Cita.as_view()),
    path('finalizar_cita/',views.Finalizar_Cita.as_view()),
]
