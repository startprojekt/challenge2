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


class DatasetRowListView(ListView):
    paginate_by = 100
    template_name = 'benford/dataset/browse_data.html'
    dataset = None

    def get(self, *args, **kwargs):
        self.dataset = Dataset.objects.get(slug=self.get_slug())
        return super(DatasetRowListView, self).get(*args, **kwargs)

    def get_queryset(self):
        return DatasetRow.objects.filter(dataset=self.dataset).order_by('line')

    def get_context_data(self, *args, **kwargs):
        ctx = super(DatasetRowListView, self).get_context_data(*args, **kwargs)
        ctx['title'] = self.get_view_title()
        ctx['dataset'] = self.dataset
        ctx['slug'] = self.get_slug()
        return ctx

    def get_slug(self):
        return self.kwargs['slug']

    def get_view_title(self):
        return f'Browse: {self.dataset.display_title()}'
