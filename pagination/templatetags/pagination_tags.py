from django import template
from django.core.paginator import Paginator, Page

from pagination.conf import PAGINATION_DEFAULT_OFFSET

register = template.Library()


def get_page_number_range(page_number: int, page_max: int, offset: int = None):
    offset = offset or PAGINATION_DEFAULT_OFFSET
    page_from = page_number - offset if page_number > offset else 1
    page_to = page_number + offset if page_number <= page_max - offset else page_max
    return range(page_from, page_to + 1)


@register.inclusion_tag('pagination/templatetags/pagination.html')
def pagination(paginator: Paginator, page_obj: Page, offset: int = None):
    return {
        'paginator': paginator,
        'page_obj': page_obj,
        'page_number_range': get_page_number_range(
            page_obj.number, paginator.num_pages, offset=offset),
    }
