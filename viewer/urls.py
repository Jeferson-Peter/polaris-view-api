from django.urls import path
from .views import DataFileUploadView, DataFileListView, DataFileDetailView

urlpatterns = [
    path('upload/', DataFileUploadView.as_view(), name='upload_datafile'),
    path('files/', DataFileListView.as_view(), name='list_datafiles'),
    path('files/<int:pk>/', DataFileDetailView.as_view(), name='detail_datafile'),
]
