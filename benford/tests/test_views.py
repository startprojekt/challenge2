import re

from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.test.testcases import TestCase

from benford.models import Dataset
from benford.views import DatasetUploadView, DatasetDetailView, DashboardView


class ViewsTest(TestCase):
    def test_dashboard_view(self):
        request = RequestFactory().get('/')
        view = DashboardView()
        view.setup(request)
        response = view.dispatch(request)
        context_data = view.get_context_data()
        self.assertIn('page_obj', context_data)

    def test_upload_view(self):
        request = RequestFactory().post('/upload/', data={
            'data_raw': '1',
        })
        view = DatasetUploadView()
        view.setup(request)
        response = view.dispatch(request)
        self.assertIsNotNone(view.object)
        self.assertIsNotNone(re.match(r'[a-z]{10}', view.object.slug))
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_detail_view(self):
        self.assertEqual(Dataset.objects.count(), 0)
        Dataset.objects.create(title='My title', slug='abcdefghij')
        request = RequestFactory().get('/dataset/abcdefghij/', )
        view = DatasetDetailView()
        view.setup(request, slug='abcdefghij')
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)

        context = view.get_context_data()
        self.assertIn('title', context)
        self.assertEqual(context['title'], 'My title')

        self.assertIn('significant_digits', context)
