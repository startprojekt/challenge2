from django.urls import path

from benford.views import DashboardView, DatasetUploadView, DatasetDetailView, DatasetRowListView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('upload/', DatasetUploadView.as_view(), name='upload_dataset'),
    path('dataset/<slug:slug>/', DatasetDetailView.as_view(), name='dataset_detail'),
    path('dataset/<slug:slug>/browse/', DatasetRowListView.as_view(), name='dataset_rows'),
]

app_name = 'benford'
