from django.urls import path, include
from . import views
from .views import RegisterAPIView, UserDetailAPIView, DeleteSessionImagesAPIView, LatestSessionResultsAPIView, UserSessionsAPIView, DeleteAnalysisSessionAPIView, SessionResultsAPIView, UpdateSessionNameAPIView, DownloadSessionImagesAPIView, EmailAuthTokenAPIView, ResetPasswordAPIView

app_name = 'necrosis'
urlpatterns = [
    path('', views.index, name='index'),
    path('image_upload/', views.ImageUploadAPIView.as_view(), name='image_upload'),
    path('upload/', views.upload_image_view, name='upload_image'),
    path('api/analyze/', views.AnalyzeImagesAPIView.as_view(), name='analyze_images'),
    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/login/', EmailAuthTokenAPIView.as_view(), name='login'),
    path('api/user/<str:email>/', UserDetailAPIView.as_view(), name='user_detail'),
    path('api/delete_session_images/', DeleteSessionImagesAPIView.as_view(), name='delete_session_images'),
    path('api/latest_session_results/', LatestSessionResultsAPIView.as_view(), name='latest_session_results'),
    path('api/user_sessions/', UserSessionsAPIView.as_view(), name='user_sessions'),
    path('api/sessions/<str:session_id>/', DeleteAnalysisSessionAPIView.as_view(), name='delete_analysis_session'),
    path('api/session_results/<str:session_id>/', SessionResultsAPIView.as_view(), name='session_results'),
    path('api/sessions/<str:session_id>/name/', UpdateSessionNameAPIView.as_view(), name='update_session_name'),
    path('api/sessions/<str:session_id>/download_images/', DownloadSessionImagesAPIView.as_view(), name='download_session_images'),
    path('api/reset_password/', ResetPasswordAPIView.as_view(), name='reset_password'),
]
