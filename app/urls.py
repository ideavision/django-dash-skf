from django.urls import path
from app import views
app_name = 'app'
urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('dash/create/', views.dash_create, name='dash_create'),
    path('dash/multiple-create/', views.dash_multiple_create, name='dash_multiple_create'), # New
    path('dash/<str:dash_uid>/', views.dash_show, name='dash_show'),

]
