from django.core.paginator import Paginator
from django.template import Context, Template
from django.test import SimpleTestCase

from pagination.templatetags.pagination_tags import get_page_number_range


class PaginationTest(SimpleTestCase):
    def test_page_range(self):
        self.assertListEqual(
            list(get_page_number_range(page_number=1, page_max=1, offset=3)),
            [1, ])

        self.assertListEqual(
            list(get_page_number_range(page_number=1, page_max=2, offset=3)),
            [1, 2])

        self.assertListEqual(
            list(get_page_number_range(page_number=1, page_max=3, offset=3)),
            [1, 2, 3])

        self.assertListEqual(
            list(get_page_number_range(page_number=3, page_max=10, offset=3)),
            [1, 2, 3, 4, 5, 6])

        self.assertListEqual(
            list(get_page_number_range(page_number=3, page_max=5, offset=1)),
            [2, 3, 4])

    def test_render(self):
        object_list = list(range(0, 100))
        paginator = Paginator(object_list=object_list, per_page=10)
        t = Template('{% load pagination_tags %}{% pagination paginator page_obj %}')
        context = Context({
            'paginator': paginator,
            'page_obj': paginator.get_page(1),
        })
        html = t.render(context)

        self.assertIn('<nav class="nav-pagination">', html)
