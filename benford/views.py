from django.shortcuts import redirect
from django.views.generic import FormView, DetailView, ListView

from benford.analyzer import BenfordAnalyzer
from benford.forms import DatasetUploadForm
from benford.models import Dataset, DatasetRow


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
    analyzer: BenfordAnalyzer = None

    def get_object(self, queryset=None):
        obj = super(DatasetDetailView, self).get_object(queryset=queryset)
        self.analyzer = BenfordAnalyzer.create_from_model(obj)
        return obj

    def get_context_data(self, **kwargs):
        self.object: Dataset
        ctx = super(DatasetDetailView, self).get_context_data(**kwargs)
        ctx['title'] = self.object.title
        ctx['significant_digits'] = self.object.significant_digits.all().order_by('digit')
        ctx['analyzer'] = self.analyzer
        ctx['dataset_rows'] = self.get_erroneous_dataset_rows()
        return ctx

    def get_erroneous_dataset_rows(self):
        return DatasetRow.objects.filter(
            dataset=self.analyzer.dataset, has_error=True,
        ).order_by('line')
