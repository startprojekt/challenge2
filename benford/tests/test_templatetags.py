from django.template import Context, Template
from django.test import TestCase

from benford.analyzer import BenfordAnalyzer


class TemplateTagsTest(TestCase):
    def setUp(self):
        pass

    def test_matplotlib_graph(self):
        analyzer = BenfordAnalyzer(occurences={1: 10, 2: 5, 3: 3})
        analyzer.save()
        context = Context({'analyzer': analyzer})
        template = Template('{% load benford_tags %}{% graph analyzer %}')
        html = template.render(context)

        # We should get an image.
        self.assertIn('<img', html)
        self.assertTrue(html.startswith('<img'))

        # The image should have source in base64 format.
        self.assertIn('data:image/png;base64,', html)
