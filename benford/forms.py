import magic
from crispy_forms.layout import Layout, Submit, Field, Div
from django import forms
from pydash import get

from crispy_forms_bootstrap5.forms import CrispyFormMixin


class DatasetUploadForm(CrispyFormMixin, forms.Form):
    title = forms.CharField(required=False, label="Your dataset name")
    data_file = forms.FileField(
        required=False, label="Upload data file...")
    data_raw = forms.CharField(
        label="...or paste your data here",
        widget=forms.Textarea(), required=False,
    )
    relevant_column = forms.IntegerField(
        min_value=0, required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Auto'}))
    has_header = forms.BooleanField(
        required=False,
        label="Is first row a header?")

    def clean(self):
        data_file = get(self.cleaned_data, 'data_file')
        data_raw = get(self.cleaned_data, 'data_raw')
        if not (data_file or data_raw):
            self.add_error(None, forms.ValidationError('Please provide either file or raw data.'))
        return super(DatasetUploadForm, self).clean()

    def clean_data_file(self):
        file = self.cleaned_data['data_file']
        if file is not None:
            file_type = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)
            if not file_type.startswith('text/'):
                self.add_error('data_file', 'Uploaded file must be a text file.')
        return file

    def get_form_layout(self) -> Layout:
        return Layout(
            Div(
                Field('title', css_class='form-control'),
                css_class='row my-3',
            ),
            Div(
                Field('data_file', css_class='form-control'),
                css_class='row my-3',
            ),
            Div(
                Field('data_raw', css_class='form-control'),
                css_class='row my-3',
            ),
            Div(
                Div(
                    Field('relevant_column', css_class='form-control'),
                    css_class='col-12 col-md-6',
                ),
                Div(
                    Div(Field('has_header', css_class='form-check-input'), css_class='form-check'),
                    css_class='col-12 col-md-6',
                ),
                css_class='row my-3 align-items-end',
            ),
            Submit(name='submit', value='Send form', css_id='id_submit'),
        )

    @property
    def form_id(self) -> str:
        return 'form-upload-dataset'
