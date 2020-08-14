from django.urls import path

from benford.views import DashboardView, DatasetUploadView, DatasetDetailView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('upload/', DatasetUploadView.as_view(), name='upload_dataset'),
    path('dataset/<slug:slug>/', DatasetDetailView.as_view(), name='dataset_detail'),
]

app_name = 'benford'
