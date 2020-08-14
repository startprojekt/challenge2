from django import forms
from pydash import get

from benford.models import Dataset


class DatasetUploadForm(forms.ModelForm):
    data_file = forms.FileField(required=False)
    data_raw = forms.CharField(widget=forms.Textarea(), required=False)

    def clean(self):
        data_file = get(self.cleaned_data, 'data_file')
        data_raw = get(self.cleaned_data, 'data_raw')
        if not (data_file or data_raw):
            raise forms.ValidationError('Please provide either file or raw data.')
        return super(DatasetUploadForm, self).clean()

    class Meta:
        model = Dataset
        fields = ['title', 'data_file', 'data_raw', ]
