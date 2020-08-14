from django.urls import path

from benford.views import DashboardView, UploadDatasetView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('upload', UploadDatasetView.as_view(), name='upload_dataset'),
]

app_name = 'benford'
