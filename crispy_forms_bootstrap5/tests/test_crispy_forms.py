from crispy_forms.layout import Layout
from django.test import SimpleTestCase

from crispy_forms_bootstrap5.forms import CrispyFormMixin


class CrispyFormMixinTest(SimpleTestCase):
    def test_crispy(self):
        with self.assertRaises(NotImplementedError):
            CrispyFormMixin()

        class SomeForm(CrispyFormMixin):
            def get_form_layout(self) -> Layout:
                return Layout()

        f = SomeForm()
        self.assertEqual(f.form_id, 'id_form')
