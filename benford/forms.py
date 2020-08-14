from crispy_forms.layout import Layout, Submit
from django import forms
from pydash import get

from crispy_forms_bootstrap5.forms import CrispyFormMixin


class DatasetUploadForm(CrispyFormMixin, forms.Form):
    title = forms.CharField(required=False)
    data_file = forms.FileField(required=False)
    data_raw = forms.CharField(widget=forms.Textarea(), required=False)
    relevant_column = forms.IntegerField(min_value=0, required=False)
    has_header = forms.BooleanField(required=False)

    def clean(self):
        data_file = get(self.cleaned_data, 'data_file')
        data_raw = get(self.cleaned_data, 'data_raw')
        if not (data_file or data_raw):
            self.add_error(None, forms.ValidationError('Please provide either file or raw data.'))
        return super(DatasetUploadForm, self).clean()

    def get_form_layout(self) -> Layout:
        return Layout(
            'title',
            'data_file',
            'data_raw',
            'relevant_column',
            'has_header',
            Submit(name='submit', value='Send form', css_id='id_submit'),
        )

    @property
    def form_id(self) -> str:
        return 'form-upload-dataset'
