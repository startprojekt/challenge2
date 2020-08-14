from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class CrispyFormMixin:
    def __init__(self, *args, **kwargs):
        super(CrispyFormMixin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.use_custom_control = False
        self.helper.layout = self.get_form_layout()

    def get_form_layout(self) -> Layout:
        raise NotImplementedError
