from django.conf import settings

DEFAULT_BASE = getattr(settings, 'BENFORD_DEFAULT_BASE', 10)

# Assessment whether given data is statistically significant.
# Value taken from:
# https://ib.bioninja.com.au/higher-level/topic-10-genetics-and-evolu/102-inheritance/chi-squared-table.html
# Not sure here... :(
BENFORD_LAW_COMPLIANCE_STAT_SIG = 14.68
