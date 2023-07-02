'''
Apps level api endpoint urls
'''
from django.urls import path
from apps.video_streaming import views

urlpatterns = [
    path('videolistcreate/', views.VideoListCreateAPIView.as_view(), name='videolistcreate'),
    path('videodetail/<int:pk>', views.VideoUpdateDeleteAPIView.as_view(), name='videodetail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('video_stream/', views.video_stream, name='video_stream'),
    path('start_stream/<str:video_path>/', views.start_stream, name='start_stream'),
    path('create_video/', views.create_video, name='create_video'),
    path('update_video/<int:video_id>/', views.update_video, name='update_video'),
    path('delete_video/<int:video_id>/', views.delete_video, name='delete_video'),
]
