from django.urls import path

from benford.views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]

app_name = 'benford'
