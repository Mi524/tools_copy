from django.urls import path

from . import views

app_name = "basic_tables"

urlpatterns = [
    # 人力安排详情表
    path('', views.index, name='index'),
    path('upload_inputdata/', views.upload_inputdata, name='upload_inputdata'),
    path('clear_inputdata/', views.clear_inputdata, name='clear_inputdata'),
    path('info_team/', views.info_team, name='info_team'),
    path('upload_team/', views.upload_team, name='upload_team'),
]
