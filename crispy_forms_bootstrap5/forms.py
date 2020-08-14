from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class CrispyFormMixin:
    def __init__(self, *args, **kwargs):
        super(CrispyFormMixin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'POST'
        self.helper.form_id = self.form_id
        self.helper.use_custom_control = False
        self.helper.layout = self.get_form_layout()

    def get_form_layout(self) -> Layout:
        raise NotImplementedError

    @property
    def form_id(self) -> str:
        return 'id_form'
