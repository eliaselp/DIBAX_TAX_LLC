from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
    path('home/', views.Index.as_view()),
]
