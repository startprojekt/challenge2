from django.conf import settings

PAGINATION_DEFAULT_OFFSET = getattr(settings, 'PAGINATION_DEFAULT_OFFSET', 3)
