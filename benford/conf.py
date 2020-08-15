from django.conf import settings

DEFAULT_BASE = getattr(settings, 'BENFORD_DEFAULT_BASE', 10)
