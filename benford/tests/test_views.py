import re

from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.test.testcases import TestCase

from benford.views import DatasetUploadView


class ViewsTest(TestCase):
    def test_upload_view(self):
        request = RequestFactory().post("/upload/", data={
            'data_raw': '1',
        })
        view = DatasetUploadView()
        view.setup(request)
        response = view.dispatch(request)
        self.assertIsNotNone(view.object)
        self.assertIsNotNone(re.match(r'[a-z]{10}', view.object.slug))
        self.assertIsInstance(response, HttpResponseRedirect)
