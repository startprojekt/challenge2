from django.contrib.admindocs.views import ModelDetailView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, DetailView, ListView

from benford.core import BenfordAnalyzer
from benford.forms import DatasetUploadForm
from benford.models import Dataset


class DashboardView(ListView):
    template_name = 'benford/dashboard.html'
    queryset = Dataset.objects.all()
    paginate_by = 10


class DatasetUploadView(FormView):
    template_name = 'benford/form.html'
    form_class = DatasetUploadForm

    def __init__(self, *args, **kwargs):
        self.object = None
        super(DatasetUploadView, self).__init__(*args, **kwargs)

    def create_dataset(self, form):
        benford_analyzer = BenfordAnalyzer.create_from_form(form)
        self.object = benford_analyzer.save()

    def form_valid(self, form):
        self.create_dataset(form)
        return redirect('benford:dataset_detail', slug=self.object.slug)


class DatasetDetailView(DetailView):
    template_name = 'benford/dataset/detail.html'
    model = Dataset

    def get_context_data(self, **kwargs):
        ctx = super(DatasetDetailView, self).get_context_data(**kwargs)
        ctx['title'] = self.object.title
        return ctx
