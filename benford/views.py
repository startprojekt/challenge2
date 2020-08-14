from django.shortcuts import render
from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'benford/dashboard.html'


class UploadDatasetView(TemplateView):
    template_name = 'benford/form.html'
