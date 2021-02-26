from django.urls import path

from . import views

app_name = "basic_tables"

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_inputdata/', views.upload_inputdata, name='upload_inputdata'),
    path('clear_inputdata/', views.clear_inputdata, name='clear_inputdata'),
]
